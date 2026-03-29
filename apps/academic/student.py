from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import BaseNamedCodeModel, tenant_id_from_user

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
        (1, "1º Ciclo"),
        (2, "2º Ciclo"),
    ]
    ESTADO_CHOICES = [
        ("active", "Ativo"),
        ("graduado", "Graduado"),
        ("retido", "Retido"),
        ("transferido", "Transferido"),
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
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="active", verbose_name="Estado")
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
        "learning.Course",
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
    identification_document_name = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        verbose_name="Nome do documento de identificação",
        help_text="Nome amigável do ficheiro enviado (ex.: BI do aluno).",
    )
    previous_certificate = models.FileField(
        upload_to="students/certificates/",
        null=True,
        blank=True,
        verbose_name="Certificado/declaração da classe anterior",
    )
    previous_certificate_name = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        verbose_name="Nome do certificado/declaração anterior",
        help_text="Nome amigável do certificado ou declaração enviada.",
    )
    competencies = models.ManyToManyField("curriculum.Competency", through="StudentCompetency", verbose_name="Competências")
    courses = models.ManyToManyField("learning.Course", related_name="students", blank=True, verbose_name="Cursos")

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

    def _populate_document_names(self):
        if self.identification_document and not (self.identification_document_name or "").strip():
            self.identification_document_name = (self.identification_document.name or "").split("/")[-1]
        if self.previous_certificate and not (self.previous_certificate_name or "").strip():
            self.previous_certificate_name = (self.previous_certificate.name or "").split("/")[-1]

    def clean(self):
        self._populate_document_names()
        profile_tenant_id = tenant_id_from_user(self.user)
        if profile_tenant_id:
            if self.tenant_id and self.tenant_id != profile_tenant_id:
                raise ValidationError({"tenant_id": "O tenant do aluno deve coincidir com o tenant do perfil do usuário vinculado."})
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id é obrigatório. Envie o header X-Tenant-ID ou configure tenant_id no seu perfil (UserProfile)."})
        if self.grade is None:
            raise ValidationError({"grade": "A classe é obrigatória."})
        if not 1 <= self.grade <= 12:
            raise ValidationError({"grade": "A grade deve estar entre 1 e 12."})
        self.cycle = self.cycle_for_grade(self.grade)
        if not self.cycle_model_id:
            self.cycle_model = self.cycle_model_for_grade(self.grade)

        if self.grade == 1:
            if not self.identification_document:
                raise ValidationError({"identification_document": "Anexe o documento de identificação (1ª classe)."})
        elif self.grade >= 2:
            if not self.identification_document:
                raise ValidationError({"identification_document": "Anexe o documento de identificação."})
            if not self.previous_certificate:
                raise ValidationError({"previous_certificate": "Anexe o certificado/declaração da classe anterior."})

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

        if self.pk:
            for course in self.courses.all():
                course_tenant = (course.tenant_id or "").strip()
                if course_tenant and course_tenant != (self.tenant_id or "").strip():
                    raise ValidationError({"courses": _("Todos os cursos devem pertencer ao mesmo tenant do aluno.")})

    def save(self, *args, **kwargs):
        self._populate_document_names()
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
        ordering = ["name"]
