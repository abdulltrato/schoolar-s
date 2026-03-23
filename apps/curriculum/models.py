from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from apps.school.models import Grade


class CurriculumArea(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nome")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Área curricular"
        verbose_name_plural = "Áreas curriculares"


class Subject(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nome")
    area = models.ForeignKey(CurriculumArea, on_delete=models.CASCADE, verbose_name="Área")
    cycle = models.IntegerField(verbose_name="Ciclo")

    def clean(self):
        if self.cycle not in {1, 2}:
            raise ValidationError({"cycle": "The subject cycle must be 1 or 2."})

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


class Competency(models.Model):
    AREA_CHOICES = [
        ("language_communication", "Linguagem e comunicação"),
        ("scientific_technological_knowledge", "Saber científico e tecnológico"),
        ("reasoning_problem_solving", "Raciocínio e resolução de problemas"),
        ("personal_development_autonomy", "Desenvolvimento pessoal e autonomia"),
        ("interpersonal_relationship", "Relacionamento interpessoal"),
        ("wellbeing_health_environment", "Bem-estar, saúde e ambiente"),
        ("aesthetic_artistic_sensitivity", "Sensibilidade estética e artística"),
    ]
    LEGACY_AREA_MAP = {
        "linguagem_comunicacao": "language_communication",
        "saber_cientifico_tecnologico": "scientific_technological_knowledge",
        "raciocinio_resolucao_problemas": "reasoning_problem_solving",
        "desenvolvimento_pessoal_autonomia": "personal_development_autonomy",
        "relacionamento_interpessoal": "interpersonal_relationship",
        "bem_estar_saude_ambiente": "wellbeing_health_environment",
        "sensibilidade_estetica_artistica": "aesthetic_artistic_sensitivity",
    }

    name = models.CharField(max_length=200, verbose_name="Nome")
    description = models.TextField(blank=True, verbose_name="Descrição")
    area = models.CharField(max_length=50, choices=AREA_CHOICES, verbose_name="Área")
    cycle = models.IntegerField(verbose_name="Ciclo")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Disciplina")
    grade = models.ForeignKey(Grade, null=True, blank=True, on_delete=models.PROTECT, verbose_name="Classe")

    def __init__(self, *args, **kwargs):
        area = kwargs.get("area")
        if area is not None:
            kwargs["area"] = self.LEGACY_AREA_MAP.get(area, area)
        super().__init__(*args, **kwargs)

    def clean(self):
        self.area = self.LEGACY_AREA_MAP.get(self.area, self.area)
        if self.cycle not in {1, 2}:
            raise ValidationError({"cycle": "The competency cycle must be 1 or 2."})
        if self.subject and self.subject.cycle != self.cycle:
            raise ValidationError({"subject": "The subject must belong to the same cycle as the competency."})
        if self.grade_id:
            self.cycle = self.grade.cycle

    def save(self, *args, **kwargs):
        self.area = self.LEGACY_AREA_MAP.get(self.area, self.area)
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Competência"
        verbose_name_plural = "Competências"
        ordering = ["name"]


class BaseCurriculum(models.Model):
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


class LocalCurriculum(models.Model):
    tenant_id = models.CharField(max_length=50, verbose_name="Identificador do tenant")
    cycle = models.IntegerField(verbose_name="Ciclo")
    additional_competencies = models.ManyToManyField(Competency, blank=True, verbose_name="Competências adicionais")

    def clean(self):
        if self.cycle not in {1, 2}:
            raise ValidationError({"cycle": "The local curriculum cycle must be 1 or 2."})
        if not self.tenant_id.strip():
            raise ValidationError({"tenant_id": "tenant_id is required."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Local curriculum {self.tenant_id} cycle {self.cycle}"

    class Meta:
        verbose_name = "Currículo local"
        verbose_name_plural = "Currículos locais"
        ordering = ["tenant_id", "cycle"]


class SubjectCurriculumPlan(models.Model):
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
            self.validate_competencies(self.planned_competencies.all())

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.full_clean()
        return self

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
