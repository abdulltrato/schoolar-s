from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import BaseNamedCodeModel, tenant_id_from_user

# Modelo principal de aluno.
class Student(BaseNamedCodeModel):
    """Registro de aluno com dados acadêmicos, documentos e trilhos de ensino."""
    # Prefixo para geração automática de códigos.
    CODE_PREFIX = "STD"
    # Não herda tenant automaticamente de nenhum campo de usuário.
    TENANT_INHERIT_USER_FIELDS: tuple[str, ...] = ()

    # Opções de ramo de ensino.
    EDUCATION_PATH_CHOICES = [
        ("general", "Ensino geral"),
        ("technical", "Ensino técnico profissional"),
    ]
    # Opções de nível técnico.
    TECHNICAL_LEVEL_CHOICES = [
        ("basic", "Técnico básico"),
        ("medium", "Técnico médio"),
        ("superior", "Técnico superior"),
    ]
    # Opções de ciclo escolar.
    CICLO_CHOICES = [
        (1, "1º Ciclo"),
        (2, "2º Ciclo"),
    ]
    # Opções de estado do aluno.
    ESTADO_CHOICES = [
        ("active", "Ativo"),
        ("graduado", "Graduado"),
        ("retido", "Retido"),
        ("transferido", "Transferido"),
    ]

    # Usuário vinculado ao aluno (opcional).
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Usuário",
    )
    # Data de nascimento.
    birth_date = models.DateField(verbose_name="Data de nascimento")
    # Classe/ano do aluno.
    grade = models.IntegerField(verbose_name="Classe")
    # Ciclo (campo redundante calculado).
    cycle = models.IntegerField(choices=CICLO_CHOICES, verbose_name="Ciclo")
    # FK para modelo de ciclo detalhado.
    cycle_model = models.ForeignKey(
        "school.Cycle",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="students",
        verbose_name="Ciclo (model)",
    )
    # Estado administrativo do aluno.
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="active", verbose_name="Estado")
    # Ramo de ensino escolhido.
    education_path = models.CharField(
        max_length=20,
        choices=EDUCATION_PATH_CHOICES,
        default="general",
        verbose_name="Ramo de ensino",
    )
    # Nível técnico (somente para ensino técnico).
    technical_level = models.CharField(
        max_length=20,
        choices=TECHNICAL_LEVEL_CHOICES,
        null=True,
        blank=True,
        verbose_name="Nível técnico",
    )
    # Curso técnico associado (quando aplicável).
    technical_course = models.ForeignKey(
        "learning.Course",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="technical_students",
        verbose_name="Curso técnico",
    )
    # Documento de identificação enviado.
    identification_document = models.FileField(
        upload_to="students/identification/",
        null=True,
        blank=True,
        verbose_name="Documento de identificação (PDF/Imagem)",
    )
    # Nome amigável para o documento de identificação.
    identification_document_name = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        verbose_name="Nome do documento de identificação",
        help_text="Nome amigável do ficheiro enviado (ex.: BI do aluno).",
    )
    # Certificado ou declaração da classe anterior.
    previous_certificate = models.FileField(
        upload_to="students/certificates/",
        null=True,
        blank=True,
        verbose_name="Certificado/declaração da classe anterior",
    )
    # Nome amigável para o certificado anterior.
    previous_certificate_name = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        verbose_name="Nome do certificado/declaração anterior",
        help_text="Nome amigável do certificado ou declaração enviada.",
    )
    # Competências vinculadas via modelo intermediário.
    competencies = models.ManyToManyField("curriculum.Competency", through="StudentCompetency", verbose_name="Competências")
    # Cursos em que o aluno está inscrito.
    courses = models.ManyToManyField("learning.Course", related_name="students", blank=True, verbose_name="Cursos")

    @staticmethod
    def education_level_for_grade(grade: int) -> str:
        # Retorna nível de ensino (primário/secundário) baseado na classe.
        if grade is None:
            return ""
        return "primario" if grade <= 6 else "secundario"

    @staticmethod
    def cycle_for_grade(grade: int) -> int:
        # Determina o ciclo numérico a partir da classe.
        if grade is None:
            return 0
        if grade <= 3 or 7 <= grade <= 9:
            return 1
        return 2

    @staticmethod
    def cycle_model_for_grade(grade: int):
        # Importa aqui para evitar dependência circular.
        from apps.school.models import Cycle

        # Sem classe definida não há ciclo.
        if grade is None:
            return None
        # Mapeia faixa de classes para código de ciclo.
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
        # Retorna o objeto Cycle correspondente ao código.
        return Cycle.objects.filter(code=code).first()

    @property
    def education_level(self) -> str:
        # Propriedade calculada que usa o helper acima.
        return self.education_level_for_grade(self.grade)

    def _populate_document_names(self):
        # Preenche nomes amigáveis se o arquivo foi enviado mas o nome está vazio.
        if self.identification_document and not (self.identification_document_name or "").strip():
            self.identification_document_name = (self.identification_document.name or "").split("/")[-1]
        if self.previous_certificate and not (self.previous_certificate_name or "").strip():
            self.previous_certificate_name = (self.previous_certificate.name or "").split("/")[-1]

    def clean(self):
        # Preenche nomes de documentos antes da validação.
        self._populate_document_names()
        # Obtém tenant do perfil de usuário vinculado.
        profile_tenant_id = tenant_id_from_user(self.user)
        # Se houver tenant no perfil, garante consistência.
        if profile_tenant_id:
            if self.tenant_id and self.tenant_id != profile_tenant_id:
                raise ValidationError({"tenant_id": "O tenant do aluno deve coincidir com o tenant do perfil do usuário vinculado."})
        # Garante que tenant esteja presente.
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id é obrigatório. Envie o header X-Tenant-ID ou configure tenant_id no seu perfil (UserProfile)."})
        # Classe é obrigatória.
        if self.grade is None:
            raise ValidationError({"grade": "A classe é obrigatória."})
        # Limita faixa válida de classe.
        if not 1 <= self.grade <= 12:
            raise ValidationError({"grade": "A grade deve estar entre 1 e 12."})
        # Atualiza ciclo a partir da classe.
        self.cycle = self.cycle_for_grade(self.grade)
        # Ajusta cycle_model se ainda não estiver definido.
        if not self.cycle_model_id:
            self.cycle_model = self.cycle_model_for_grade(self.grade)

        # Valida presença de documentos obrigatórios conforme a classe.
        if self.grade == 1:
            if not self.identification_document:
                raise ValidationError({"identification_document": "Anexe o documento de identificação (1ª classe)."})
        elif self.grade >= 2:
            if not self.identification_document:
                raise ValidationError({"identification_document": "Anexe o documento de identificação."})
            if not self.previous_certificate:
                raise ValidationError({"previous_certificate": "Anexe o certificado/declaração da classe anterior."})

        # Regras adicionais para trilho técnico.
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

        # Se já existe registro, valida coerência de tenant nos cursos associados.
        if self.pk:
            for course in self.courses.all():
                course_tenant = (course.tenant_id or "").strip()
                if course_tenant and course_tenant != (self.tenant_id or "").strip():
                    raise ValidationError({"courses": _("Todos os cursos devem pertencer ao mesmo tenant do aluno.")})

    def save(self, *args, **kwargs):
        # Preenche nomes de documentos antes de salvar.
        self._populate_document_names()
        # Recalcula ciclo e cycle_model conforme a classe.
        if self.grade is not None:
            self.cycle = self.cycle_for_grade(self.grade)
            if not self.cycle_model_id:
                self.cycle_model = self.cycle_model_for_grade(self.grade)
        # Executa validações completas.
        self.full_clean()
        # Salva usando comportamento padrão do Django.
        return super().save(*args, **kwargs)

    def __str__(self):
        # Representa o aluno por seu nome.
        return self.name

    class Meta:
        # Textos de exibição no admin.
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"
        # Ordenação padrão por nome.
        ordering = ["name"]
