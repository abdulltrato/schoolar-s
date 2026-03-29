from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseNamedCodeModel, tenant_id_from_user

from .school import School


class Teacher(BaseNamedCodeModel):
    CODE_PREFIX = "TCH"
    TENANT_INHERIT_USER_FIELDS = ("user",)

    def __init__(self, *args, specialty_subject=None, **kwargs):
        # Backwards compatibility with legacy keyword in fixtures/tests.
        if specialty_subject is not None and "specialty" not in kwargs:
            kwargs["specialty"] = specialty_subject
        super().__init__(*args, **kwargs)

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Usuário")
    school = models.ForeignKey(
        School,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teachers",
        verbose_name="Escola",
    )
    specialty = models.ForeignKey(
        "curriculum.SubjectSpecialty",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Especialidade",
    )

    def clean(self):
        profile_tenant_id = tenant_id_from_user(self.user)
        if profile_tenant_id:
            if self.tenant_id and self.tenant_id != profile_tenant_id:
                raise ValidationError({"tenant_id": "O tenant do professor deve coincidir com o tenant do perfil do usuário."})
            if not self.tenant_id:
                self.tenant_id = profile_tenant_id

        school_tenant = (self.school.tenant_id or "").strip() if self.school_id else ""
        if school_tenant:
            if self.tenant_id and self.tenant_id != school_tenant:
                raise ValidationError({"tenant_id": "O tenant do professor deve coincidir com o tenant da escola."})
            if not self.tenant_id:
                self.tenant_id = school_tenant

        specialty_tenant = (self.specialty.tenant_id or "").strip() if self.specialty_id else ""
        if specialty_tenant:
            if self.tenant_id and self.tenant_id != specialty_tenant:
                raise ValidationError({"tenant_id": "O tenant do professor deve coincidir com o tenant da especialidade."})
            if not self.tenant_id:
                self.tenant_id = specialty_tenant

        if not self.specialty_id and not self.pk:
            raise ValidationError({"specialty": "A especialidade do professor é obrigatória."})

        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id é obrigatório."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Professor"
        verbose_name_plural = "Professores"
        ordering = ["name"]


class TeacherSpecialty(BaseNamedCodeModel):
    CODE_PREFIX = "TSY"

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="extra_specialties",
        verbose_name="Professor",
    )

    def clean(self):
        teacher_tenant = (self.teacher.tenant_id or "").strip() if self.teacher_id else ""
        if self.tenant_id and teacher_tenant and self.tenant_id != teacher_tenant:
            raise ValidationError({"tenant_id": "O tenant da especialidade deve coincidir com o tenant do professor."})
        if teacher_tenant and not self.tenant_id:
            self.tenant_id = teacher_tenant

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.teacher.name} - {self.name}"

    class Meta:
        verbose_name = "Especialidade de professor"
        verbose_name_plural = "Especialidades de professor"
        ordering = ["teacher__name", "name"]
