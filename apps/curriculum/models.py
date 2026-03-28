from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from core.models import BaseCodeModel, BaseNamedCodeModel

from apps.school.models import Grade


class CurriculumArea(BaseNamedCodeModel):
    CODE_PREFIX = "CAR"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Área curricular"
        verbose_name_plural = "Áreas curriculares"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "name"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_curriculumarea_name_per_tenant",
            ),
        ]


class Subject(BaseNamedCodeModel):
    CODE_PREFIX = "SUB"
    area = models.ForeignKey(CurriculumArea, on_delete=models.CASCADE, verbose_name="Área")
    cycle = models.IntegerField(verbose_name="Ciclo")

    def clean(self):
        area_tenant = (self.area.tenant_id or "").strip() if self.area_id else ""
        if area_tenant:
            if self.tenant_id and self.tenant_id != area_tenant:
                raise ValidationError({"tenant_id": "O tenant da disciplina deve coincidir com o tenant da área curricular."})
            if not self.tenant_id:
                self.tenant_id = area_tenant
        if self.cycle not in {1, 2}:
            raise ValidationError({"cycle": "O ciclo da disciplina deve ser 1 ou 2."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def competencia_set(self):
        return self.competency_set

    class Meta:
        verbose_name = "Disciplina"
        verbose_name_plural = "Disciplinas"
        ordering = ["name"]


class SubjectSpecialty(BaseNamedCodeModel):
    CODE_PREFIX = "SSP"
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="specialties", verbose_name="Disciplina")

    def clean(self):
        subject_tenant = (self.subject.tenant_id or "").strip() if self.subject_id else ""
        if subject_tenant:
            if self.tenant_id and self.tenant_id != subject_tenant:
                raise ValidationError({"tenant_id": "O tenant da especialidade deve coincidir com o tenant da disciplina."})
            if not self.tenant_id:
                self.tenant_id = subject_tenant

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.subject.name} - {self.name}"

    class Meta:
        verbose_name = "Especialidade por disciplina"
        verbose_name_plural = "Especialidades por disciplina"
        ordering = ["subject__name", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["subject", "name"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_subject_specialty_active",
            ),
        ]


class Competency(BaseNamedCodeModel):
    CODE_PREFIX = "COM"

    description = models.TextField(blank=True, verbose_name="Descrição")
    area = models.ForeignKey(
        CurriculumArea,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Área",
    )
    cycle = models.IntegerField(verbose_name="Ciclo")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Disciplina")
    grade = models.ForeignKey(Grade, null=True, blank=True, on_delete=models.PROTECT, verbose_name="Classe")

    def clean(self):
        subject_tenant = (self.subject.tenant_id or "").strip() if self.subject_id else ""
        area_tenant = (self.area.tenant_id or "").strip() if self.area_id else ""

        if self.subject_id and not self.area_id:
            self.area = self.subject.area
            area_tenant = (self.area.tenant_id or "").strip() if self.area_id else ""

        if self.subject_id and self.area_id and self.subject.area_id != self.area_id:
            raise ValidationError({"area": "A área deve coincidir com a área da disciplina."})

        if not self.area_id:
            raise ValidationError({"area": "Informe uma área para a competência."})

        if subject_tenant and area_tenant and subject_tenant != area_tenant:
            raise ValidationError({"tenant_id": "A disciplina e a área devem pertencer ao mesmo tenant."})

        if subject_tenant:
            if self.tenant_id and self.tenant_id != subject_tenant:
                raise ValidationError({"tenant_id": "O tenant da competência deve coincidir com o tenant da disciplina."})
            if not self.tenant_id:
                self.tenant_id = subject_tenant
        if area_tenant:
            if self.tenant_id and self.tenant_id != area_tenant:
                raise ValidationError({"tenant_id": "O tenant da competência deve coincidir com o tenant da área."})
            if not self.tenant_id:
                self.tenant_id = area_tenant

        if self.cycle not in {1, 2}:
            raise ValidationError({"cycle": "O ciclo da competência deve ser 1 ou 2."})
        if self.subject and self.subject.cycle != self.cycle:
            raise ValidationError({"subject": "A disciplina deve pertencer ao mesmo ciclo da competência."})
        if self.grade_id:
            self.cycle = self.grade.cycle

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Competência"
        verbose_name_plural = "Competências"
        ordering = ["name"]


class LearningOutcome(BaseCodeModel):
    CODE_PREFIX = "OUT"
    AUTO_CODE = False
    TAXONOMY_LEVEL_CHOICES = [
        ("remember", "Recordar"),
        ("understand", "Compreender"),
        ("apply", "Aplicar"),
        ("analyze", "Analisar"),
        ("evaluate", "Avaliar"),
        ("create", "Criar"),
    ]
    KNOWLEDGE_DIMENSION_CHOICES = [
        ("factual", "Factual"),
        ("conceptual", "Conceitual"),
        ("procedural", "Procedimental"),
        ("metacognitive", "Metacognitivo"),
    ]

    code = models.CharField(max_length=60, verbose_name="Código")
    description = models.TextField(verbose_name="Descrição")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Disciplina")
    grade = models.ForeignKey(Grade, null=True, blank=True, on_delete=models.PROTECT, verbose_name="Classe")
    cycle = models.IntegerField(verbose_name="Ciclo")
    taxonomy_level = models.CharField(max_length=20, choices=TAXONOMY_LEVEL_CHOICES, verbose_name="Nível cognitivo")
    knowledge_dimension = models.CharField(
        max_length=20,
        choices=KNOWLEDGE_DIMENSION_CHOICES,
        blank=True,
        verbose_name="Dimensão do conhecimento",
    )
    active = models.BooleanField(default=True, verbose_name="Ativo")
    competencies = models.ManyToManyField(
        Competency,
        through="CompetencyOutcome",
        related_name="learning_outcomes",
        verbose_name="Competências",
    )

    def clean(self):
        self.tenant_id = (self.tenant_id or "").strip()
        if not self.tenant_id:
            raise ValidationError({"tenant_id": "tenant_id é obrigatório. Envie o header X-Tenant-ID ou configure tenant_id no seu perfil (UserProfile)."})
        if not self.subject_id and not self.grade_id:
            raise ValidationError({"subject": "Informe uma disciplina ou classe para o resultado de aprendizagem."})

        if self.grade_id:
            self.cycle = self.grade.cycle

        if self.subject_id:
            if self.cycle and self.subject.cycle != self.cycle:
                raise ValidationError({"subject": "A disciplina deve pertencer ao mesmo ciclo."})
            self.cycle = self.subject.cycle

        if self.cycle not in {1, 2}:
            raise ValidationError({"cycle": "O ciclo deve ser 1 ou 2."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} - {self.description[:40]}"

    class Meta:
        verbose_name = "Resultado de aprendizagem"
        verbose_name_plural = "Resultados de aprendizagem"
        ordering = ["code"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "code", "subject", "grade"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_learning_outcome_active",
            ),
        ]


class CompetencyOutcome(BaseCodeModel):
    CODE_PREFIX = "COT"
    competency = models.ForeignKey(Competency, on_delete=models.CASCADE, verbose_name="Competência")
    outcome = models.ForeignKey(LearningOutcome, on_delete=models.CASCADE, verbose_name="Resultado de aprendizagem")
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=100, verbose_name="Peso")
    notes = models.CharField(max_length=255, blank=True, verbose_name="Observações")

    def clean(self):
        outcome_tenant = (self.outcome.tenant_id or "").strip() if self.outcome_id else ""
        if outcome_tenant:
            if self.tenant_id and self.tenant_id != outcome_tenant:
                raise ValidationError({"tenant_id": "O tenant do alinhamento deve coincidir com o resultado."})
            if not self.tenant_id:
                self.tenant_id = outcome_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id é obrigatório. Envie o header X-Tenant-ID ou configure tenant_id no seu perfil (UserProfile)."})
        if self.weight <= 0 or self.weight > 100:
            raise ValidationError({"weight": "O peso deve estar entre 0 e 100."})

        if self.outcome_id:
            if self.outcome.subject_id and self.competency.subject_id and self.outcome.subject_id != self.competency.subject_id:
                raise ValidationError({"competency": "A competência deve pertencer à mesma disciplina do resultado."})
            if self.outcome.grade_id and self.competency.grade_id and self.outcome.grade_id != self.competency.grade_id:
                raise ValidationError({"competency": "A competência deve pertencer à mesma classe do resultado."})
            if self.outcome.cycle and self.competency.cycle and self.outcome.cycle != self.competency.cycle:
                raise ValidationError({"competency": "A competência deve pertencer ao mesmo ciclo do resultado."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.outcome.code} - {self.competency.name}"

    class Meta:
        verbose_name = "Alinhamento competência-resultado"
        verbose_name_plural = "Alinhamentos competência-resultado"
        ordering = ["outcome__code", "competency__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "competency", "outcome"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_competency_outcome_active",
            ),
        ]


class BaseCurriculum(BaseCodeModel):
    CODE_PREFIX = "BCU"
    cycle = models.IntegerField(verbose_name="Ciclo")
    competencies = models.ManyToManyField(Competency, verbose_name="Competências")

    def clean(self):
        if self.cycle not in {1, 2}:
            raise ValidationError({"cycle": "The base curriculum cycle must be 1 or 2."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Base curriculum cycle {self.cycle}"

    class Meta:
        verbose_name = "Currículo base"
        verbose_name_plural = "Currículos base"
        ordering = ["cycle"]


class LocalCurriculum(BaseCodeModel):
    CODE_PREFIX = "LCU"
    cycle = models.IntegerField(verbose_name="Ciclo")
    additional_competencies = models.ManyToManyField(Competency, blank=True, verbose_name="Competências adicionais")

    def clean(self):
        if self.cycle not in {1, 2}:
            raise ValidationError({"cycle": "The local curriculum cycle must be 1 or 2."})
        if not self.tenant_id.strip():
            raise ValidationError({"tenant_id": "tenant_id é obrigatório. Envie o header X-Tenant-ID ou configure tenant_id no seu perfil (UserProfile)."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Local curriculum {self.tenant_id} cycle {self.cycle}"

    class Meta:
        verbose_name = "Currículo local"
        verbose_name_plural = "Currículos locais"
        ordering = ["tenant_id", "cycle"]


class SubjectCurriculumPlan(BaseCodeModel):
    CODE_PREFIX = "SCP"
    grade_subject = models.OneToOneField(
        "school.GradeSubject",
        on_delete=models.CASCADE,
        related_name="curriculum_plan",
        verbose_name="Disciplina da classe",
    )
    objectives = models.TextField(blank=True, verbose_name="Objetivos")
    planned_competencies = models.ManyToManyField(
        Competency,
        blank=True,
        related_name="curriculum_plans",
        verbose_name="Competências previstas",
    )
    methodology = models.TextField(blank=True, verbose_name="Metodologia")
    assessment_criteria = models.TextField(blank=True, verbose_name="Critérios de avaliação")
    active = models.BooleanField(default=True, verbose_name="Ativo")

    def validate_competencies(self, competencies):
        if not self.grade_subject_id:
            return

        subject_cycle = self.grade_subject.subject.cycle
        for competency in competencies:
            if competency.subject_id != self.grade_subject.subject_id:
                raise ValidationError({"planned_competencies": "All competencies must belong to the same subject."})
            if competency.cycle != subject_cycle:
                raise ValidationError({"planned_competencies": "All competencies must belong to the same cycle as the subject."})

    def clean(self):
        if self.grade_subject_id:
            grade_subject_tenant = (self.grade_subject.tenant_id or "").strip()
            if grade_subject_tenant:
                if self.tenant_id and self.tenant_id != grade_subject_tenant:
                    raise ValidationError({"tenant_id": "Curriculum plan tenant must match the grade subject tenant."})
                if not self.tenant_id:
                    self.tenant_id = grade_subject_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id é obrigatório. Envie o header X-Tenant-ID ou configure tenant_id no seu perfil (UserProfile)."})
        if self.pk:
            self.validate_competencies(self.planned_competencies.all())

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Plan {self.grade_subject.subject} - {self.grade_subject.grade}"

    class Meta:
        verbose_name = "Plano curricular por disciplina"
        verbose_name_plural = "Planos curriculares por disciplina"
        ordering = ["grade_subject__academic_year__code", "grade_subject__grade__number"]


@receiver(m2m_changed, sender=SubjectCurriculumPlan.planned_competencies.through)
def validate_planned_competencies(sender, instance, action, pk_set, **kwargs):
    if action != "pre_add" or not pk_set:
        return

    competencies = Competency.objects.filter(pk__in=pk_set)
    instance.validate_competencies(competencies)
