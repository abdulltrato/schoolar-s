from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError


class Student(models.Model):
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
    name = models.CharField(max_length=100, verbose_name="Nome")
    tenant_id = models.CharField(max_length=50, blank=True, verbose_name="Identificador do tenant")
    birth_date = models.DateField(verbose_name="Data de nascimento")
    grade = models.IntegerField(verbose_name="Classe")
    cycle = models.IntegerField(choices=CICLO_CHOICES, verbose_name="Ciclo")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='active', verbose_name="Estado")
    competencies = models.ManyToManyField('curriculum.Competency', through='StudentCompetency', verbose_name="Competências")

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

    @property
    def education_level(self) -> str:
        return self.education_level_for_grade(self.grade)

    def clean(self):
        if self.user_id and hasattr(self.user, "school_profile"):
            profile_tenant_id = (self.user.school_profile.tenant_id or "").strip()
            if profile_tenant_id and self.tenant_id and self.tenant_id != profile_tenant_id:
                raise ValidationError({"tenant_id": "Student tenant must match the linked user profile tenant."})
            if profile_tenant_id and not self.tenant_id:
                self.tenant_id = profile_tenant_id
        if not 1 <= self.grade <= 12:
            raise ValidationError({"grade": "A grade deve estar entre 1 e 12."})
        self.cycle = self.cycle_for_grade(self.grade)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"
        ordering = ['name']


class StudentCompetency(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="Aluno")
    competency = models.ForeignKey('curriculum.Competency', on_delete=models.CASCADE, verbose_name="Competência")
    nivel = models.DecimalField(max_digits=3, decimal_places=1, default=0.0, verbose_name="Nível")  # e.g., 0.0 to 5.0
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Data de atualização")

    def clean(self):
        if not 0 <= self.nivel <= 5:
            raise ValidationError({"nivel": "O nível deve estar entre 0.0 e 5.0."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        unique_together = ('student', 'competency')
        verbose_name = "Competência do aluno"
        verbose_name_plural = "Competências dos Alunos"


class Guardian(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Usuário",
    )
    name = models.CharField(max_length=100, verbose_name="Nome")
    tenant_id = models.CharField(max_length=50, blank=True, verbose_name="Identificador do tenant")
    phone = models.CharField(max_length=30, blank=True, verbose_name="Telefone")
    email = models.EmailField(blank=True, verbose_name="E-mail")
    relationship = models.CharField(max_length=60, blank=True, verbose_name="Parentesco")
    active = models.BooleanField(default=True, verbose_name="Ativo")

    def clean(self):
        if self.user_id and hasattr(self.user, "school_profile"):
            profile_tenant_id = (self.user.school_profile.tenant_id or "").strip()
            if profile_tenant_id and self.tenant_id and self.tenant_id != profile_tenant_id:
                raise ValidationError({"tenant_id": "Guardian tenant must match the linked user profile tenant."})
            if profile_tenant_id and not self.tenant_id:
                self.tenant_id = profile_tenant_id

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Encarregado"
        verbose_name_plural = "Encarregados"
        ordering = ["name"]


class StudentGuardian(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="Aluno")
    guardian = models.ForeignKey(Guardian, on_delete=models.CASCADE, verbose_name="Encarregado")
    primary_contact = models.BooleanField(default=False, verbose_name="Contato principal")
    receives_notifications = models.BooleanField(default=True, verbose_name="Recebe notificações")

    def clean(self):
        student_tenant = (self.student.tenant_id or "").strip()
        guardian_tenant = getattr(self.guardian, "tenant_id", "") or ""
        guardian_tenant = guardian_tenant.strip()
        if student_tenant and guardian_tenant and student_tenant != guardian_tenant:
            raise ValidationError("Student and guardian must belong to the same tenant.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.guardian} - {self.student}"

    class Meta:
        unique_together = ("student", "guardian")
        verbose_name = "Relação aluno-encarregado"
        verbose_name_plural = "Relações aluno-encarregado"
