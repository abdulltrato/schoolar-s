from decimal import Decimal

from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from core.models import BaseCodeModel, BaseNamedCodeModel, tenant_id_from_user
from django.utils.translation import gettext_lazy as _


class Student(BaseNamedCodeModel):

    CODE_PREFIX = "STD"
    TENANT_INHERIT_USER_FIELDS: tuple[str, ...] = ()

    EDUCATION_PATH_CHOICES = [
        ("general", "Ensino geral"),
        ("technical", "Ensino técnico profissional"),
    ]

    TECHNICAL_LEVEL_CHOICES = [
        ("basic", "Técnico básico"),
        ("medium", "Técnico médio"),
        ("superior", "Técnico superior"),
    ]

    CICLO_CHOICES = [
        (1, '1º Ciclo'),
        (2, '2º Ciclo'),
    ]

    ESTADO_CHOICES = [
        ('active', 'Ativo'),
        ('graduado', 'Graduado'),
        ('retido', 'Retido'),
        ('transferido', 'Transferido'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Usuário",
    )

    birth_date = models.DateField(verbose_name="Data de nascimento")
    grade = models.IntegerField(verbose_name="Classe")
    cycle = models.IntegerField(choices=CICLO_CHOICES, verbose_name="Ciclo")
    cycle_model = models.ForeignKey(
        "school.Cycle",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="students",
        verbose_name="Ciclo (model)",
    )
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='active', verbose_name="Estado")
    education_path = models.CharField(
        max_length=20,
        choices=EDUCATION_PATH_CHOICES,
        default="general",
        verbose_name="Ramo de ensino",
    )
    technical_level = models.CharField(
        max_length=20,
        choices=TECHNICAL_LEVEL_CHOICES,
        null=True,
        blank=True,
        verbose_name="Nível técnico",
    )
    technical_course = models.ForeignKey(
        'learning.Course',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="technical_students",
        verbose_name="Curso técnico",
    )
    identification_document = models.FileField(
        upload_to="students/identification/",
        null=True,
        blank=True,
        verbose_name="Documento de identificação (PDF/Imagem)",
    )
    previous_certificate = models.FileField(
        upload_to="students/certificates/",
        null=True,
        blank=True,
        verbose_name="Certificado/declaração da classe anterior",
    )
    competencies = models.ManyToManyField('curriculum.Competency', through='StudentCompetency', verbose_name="Competências")
    courses = models.ManyToManyField('learning.Course', related_name="students", blank=True, verbose_name="Cursos")

    @staticmethod
    def education_level_for_grade(grade: int) -> str:
        if grade is None:
            return ""
        return "primario" if grade <= 6 else "secundario"

    @staticmethod
    def cycle_for_grade(grade: int) -> int:
        if grade is None:
            return 0
        if grade <= 3 or 7 <= grade <= 9:
            return 1
        return 2

    @staticmethod
    def cycle_model_for_grade(grade: int):
        from apps.school.models import Cycle

        if grade is None:
            return None
        code = None
        if grade <= 3:
            code = "primary_cycle_1"
        elif grade <= 6:
            code = "primary_cycle_2"
        elif grade <= 9:
            code = "secondary_cycle_1"
        elif grade <= 12:
            code = "secondary_cycle_2"
        else:
            return None
        return Cycle.objects.filter(code=code).first()

    @property
    def education_level(self) -> str:
        return self.education_level_for_grade(self.grade)

    def clean(self):
        profile_tenant_id = tenant_id_from_user(self.user)
        if profile_tenant_id:
            if self.tenant_id and self.tenant_id != profile_tenant_id:
                raise ValidationError({"tenant_id": "O tenant do aluno deve coincidir com o tenant do perfil do usuário vinculado."})
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id é obrigatório. Envie o header X-Tenant-ID ou configure tenant_id no seu perfil (UserProfile)."})
        if not 1 <= self.grade <= 12:
            raise ValidationError({"grade": "A grade deve estar entre 1 e 12."})
        self.cycle = self.cycle_for_grade(self.grade)
        if not self.cycle_model_id:
            self.cycle_model = self.cycle_model_for_grade(self.grade)

        # Documentos obrigatórios conforme a classe
        if self.grade == 1:
            if not self.identification_document:
                raise ValidationError({"identification_document": "Anexe o documento de identificação (1ª classe)."})
            # Certificado anterior não é exigido na 1ª classe
        elif self.grade >= 2:
            if not self.identification_document:
                raise ValidationError({"identification_document": "Anexe o documento de identificação."})
            if not self.previous_certificate:
                raise ValidationError({"previous_certificate": "Anexe o certificado/declaração da classe anterior."})

        # Trilho técnico x geral
        if self.education_path == "technical":
            if not self.technical_level:
                raise ValidationError({"technical_level": "Selecione o nível técnico (básico, médio ou superior)."})
            if not self.technical_course_id:
                raise ValidationError({"technical_course": "Selecione o curso técnico."})
        else:
            if self.technical_level:
                raise ValidationError({"technical_level": "Remova o nível técnico para alunos do ensino geral."})
            if self.technical_course_id:
                raise ValidationError({"technical_course": "Remova o curso técnico para alunos do ensino geral."})

        # Validação de consistência de tenant nos cursos associados (somente após ter PK)
        if self.pk:
            for course in self.courses.all():
                course_tenant = (course.tenant_id or "").strip()
                if course_tenant and course_tenant != (self.tenant_id or "").strip():
                    raise ValidationError({"courses": _("Todos os cursos devem pertencer ao mesmo tenant do aluno.")})

    def save(self, *args, **kwargs):
        if self.grade is not None:
            self.cycle = self.cycle_for_grade(self.grade)
            if not self.cycle_model_id:
                self.cycle_model = self.cycle_model_for_grade(self.grade)
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"
        ordering = ['name']


class StudentCompetency(BaseCodeModel):
    CODE_PREFIX = "STC"
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="Aluno")
    competency = models.ForeignKey('curriculum.Competency', on_delete=models.CASCADE, verbose_name="Competência")
    nivel = models.DecimalField(max_digits=3, decimal_places=1, default=0.0, verbose_name="Nível")  # e.g., 0.0 to 5.0
    def clean(self):
        student_tenant = (self.student.tenant_id or "").strip() if self.student_id else ""
        if student_tenant:
            if self.tenant_id and self.tenant_id != student_tenant:
                raise ValidationError({"tenant_id": "O tenant da competência do aluno deve coincidir com o tenant do aluno."})
            if not self.tenant_id:
                self.tenant_id = student_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id é obrigatório. Envie o header X-Tenant-ID ou configure tenant_id no seu perfil (UserProfile)."})
        if not 0 <= self.nivel <= 5:
            raise ValidationError({"nivel": "O nível deve estar entre 0.0 e 5.0."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "competency"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_student_competency_active",
            ),
        ]
        verbose_name = "Competência do aluno"
        verbose_name_plural = "Competências dos Alunos"


class Guardian(BaseNamedCodeModel):
    CODE_PREFIX = "GRD"
    TENANT_INHERIT_USER_FIELDS = ("user",)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Usuário",
    )
    phone = models.CharField(max_length=30, blank=True, verbose_name="Telefone")
    email = models.EmailField(blank=True, verbose_name="E-mail")
    relationship = models.CharField(max_length=60, blank=True, verbose_name="Parentesco")
    active = models.BooleanField(default=True, verbose_name="Ativo")

    def clean(self):
        profile_tenant_id = tenant_id_from_user(self.user)
        if profile_tenant_id:
            if self.tenant_id and self.tenant_id != profile_tenant_id:
                raise ValidationError({"tenant_id": "O tenant do encarregado deve coincidir com o tenant do perfil do usuário vinculado."})
            if not self.tenant_id:
                self.tenant_id = profile_tenant_id
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id é obrigatório. Envie o header X-Tenant-ID ou configure tenant_id no seu perfil (UserProfile)."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Encarregado"
        verbose_name_plural = "Encarregados"
        ordering = ["name"]


class StudentGuardian(BaseCodeModel):
    CODE_PREFIX = "STG"
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="Aluno")
    guardian = models.ForeignKey(Guardian, on_delete=models.CASCADE, verbose_name="Encarregado")
    primary_contact = models.BooleanField(default=False, verbose_name="Contato principal")
    receives_notifications = models.BooleanField(default=True, verbose_name="Recebe notificações")

    def clean(self):
        student_tenant = (self.student.tenant_id or "").strip()
        guardian_tenant = getattr(self.guardian, "tenant_id", "") or ""
        guardian_tenant = guardian_tenant.strip()
        if student_tenant and guardian_tenant and student_tenant != guardian_tenant:
            raise ValidationError("Aluno e encarregado devem pertencer ao mesmo tenant.")
        if self.tenant_id and student_tenant and self.tenant_id != student_tenant:
            raise ValidationError({"tenant_id": "O tenant do vínculo aluno-encarregado deve coincidir com o tenant do aluno."})
        if self.tenant_id and guardian_tenant and self.tenant_id != guardian_tenant:
            raise ValidationError({"tenant_id": "O tenant do vínculo aluno-encarregado deve coincidir com o tenant do encarregado."})
        self.tenant_id = self.tenant_id or student_tenant or guardian_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id é obrigatório. Envie o header X-Tenant-ID ou configure tenant_id no seu perfil (UserProfile)."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.guardian} - {self.student}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "student", "guardian"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_student_guardian_active",
            ),
        ]
        verbose_name = "Relação aluno-encarregado"
        verbose_name_plural = "Relações aluno-encarregado"


class StudentOutcome(BaseCodeModel):
    CODE_PREFIX = "STO"
    MASTERY_CHOICES = [
        ("not_started", "Não iniciado"),
        ("developing", "Em desenvolvimento"),
        ("proficient", "Proficiente"),
        ("advanced", "Avançado"),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="Aluno")
    outcome = models.ForeignKey("curriculum.LearningOutcome", on_delete=models.CASCADE, verbose_name="Resultado de aprendizagem")
    mastery_level = models.DecimalField(max_digits=3, decimal_places=1, default=0.0, verbose_name="Nível")
    status = models.CharField(max_length=20, choices=MASTERY_CHOICES, default="not_started", verbose_name="Estado")
    evidence_count = models.PositiveIntegerField(default=0, verbose_name="Evidências")
    def clean(self):
        student_tenant = (self.student.tenant_id or "").strip() if self.student_id else ""
        outcome_tenant = (self.outcome.tenant_id or "").strip() if self.outcome_id else ""
        if student_tenant and outcome_tenant and student_tenant != outcome_tenant:
            raise ValidationError({"tenant_id": "Aluno e resultado devem pertencer ao mesmo tenant."})
        if self.tenant_id and student_tenant and self.tenant_id != student_tenant:
            raise ValidationError({"tenant_id": "O tenant deve coincidir com o do aluno."})
        if outcome_tenant and self.tenant_id and self.tenant_id != outcome_tenant:
            raise ValidationError({"tenant_id": "O tenant deve coincidir com o do resultado."})
        self.tenant_id = self.tenant_id or student_tenant or outcome_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id é obrigatório. Envie o header X-Tenant-ID ou configure tenant_id no seu perfil (UserProfile)."})
        if not 0 <= self.mastery_level <= 5:
            raise ValidationError({"mastery_level": "O nível deve estar entre 0.0 e 5.0."})

    @staticmethod
    def _status_for_mastery(level: Decimal) -> str:
        if level >= Decimal("4.5"):
            return "advanced"
        if level >= Decimal("3.0"):
            return "proficient"
        if level >= Decimal("1.0"):
            return "developing"
        return "not_started"

    @classmethod
    def recalculate_for_components(cls, *, student, component_ids):
        component_ids = [component_id for component_id in component_ids if component_id]
        if not component_ids:
            return
        from apps.assessment.models import AssessmentOutcomeMap

        outcome_ids = list(
            AssessmentOutcomeMap.objects.filter(component_id__in=component_ids, active=True)
            .values_list("outcome_id", flat=True)
            .distinct()
        )
        if outcome_ids:
            cls.recalculate_for_outcomes(student=student, outcome_ids=outcome_ids)

    @classmethod
    def recalculate_for_outcomes(cls, *, student, outcome_ids):
        if not outcome_ids:
            return
        from apps.assessment.models import Assessment, AssessmentOutcomeMap

        mappings = list(
            AssessmentOutcomeMap.objects.filter(outcome_id__in=outcome_ids, active=True).select_related("component")
        )
        if not mappings:
            return

        outcome_components = {}
        component_ids = set()
        for mapping in mappings:
            outcome_components.setdefault(mapping.outcome_id, {})[mapping.component_id] = Decimal(mapping.weight)
            component_ids.add(mapping.component_id)

        assessments = Assessment.objects.filter(
            student=student,
            component_id__in=component_ids,
            score__isnull=False,
        ).select_related("component")

        assessments_by_component = {}
        for assessment in assessments:
            assessments_by_component.setdefault(assessment.component_id, []).append(assessment)

        for outcome_id, component_weights in outcome_components.items():
            total_weight = Decimal("0")
            weighted_total = Decimal("0")
            evidence_count = 0

            for component_id, weight in component_weights.items():
                if weight <= 0:
                    continue
                for assessment in assessments_by_component.get(component_id, []):
                    max_score = Decimal(assessment.component.max_score)
                    if max_score <= 0:
                        continue
                    score = Decimal(assessment.score)
                    normalized = (score / max_score) * Decimal("20")
                    weighted_total += normalized * weight
                    total_weight += weight
                    evidence_count += 1

            if total_weight <= 0:
                cls.all_objects.filter(student=student, outcome_id=outcome_id).update(
                    mastery_level=Decimal("0.0"),
                    status="not_started",
                    evidence_count=0,
                    deleted_at=None,
                )
                continue

            average = weighted_total / total_weight
            mastery = (average / Decimal("20")) * Decimal("5")
            mastery = mastery.quantize(Decimal("0.1"))
            status = cls._status_for_mastery(mastery)
            tenant_id = (student.tenant_id or "").strip()

            cls.all_objects.update_or_create(
                student=student,
                outcome_id=outcome_id,
                defaults={
                    "tenant_id": tenant_id,
                    "mastery_level": mastery,
                    "status": status,
                    "evidence_count": evidence_count,
                    "deleted_at": None,
                },
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.outcome.code}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "student", "outcome"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_student_outcome_active",
            ),
        ]
        verbose_name = "Resultado do aluno"
        verbose_name_plural = "Resultados do aluno"
        ordering = ["-updated_at"]
