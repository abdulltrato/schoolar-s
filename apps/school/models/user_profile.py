from django.conf import settings
# Configurações (AUTH_USER_MODEL).
from django.core.exceptions import ValidationError
# Exceção de validação.
from django.db import models
# Campos do ORM.

from core.models import BaseCodeModel
# Modelo base com código e auditoria.

from .school import School
# Escola associada ao perfil (quando aplicável).


class UserProfile(BaseCodeModel):
    """Perfil escolar associado a um usuário, com papel e escopo de localização."""

    CODE_PREFIX = "UPR"
    ROLE_CHOICES = [
        ("national_admin", "Administrador nacional"),
        ("provincial_admin", "Administrador provincial"),
        ("district_admin", "Administrador distrital"),
        ("school_director", "Diretor da escola"),
        ("teacher", "Professor"),
        ("student", "Aluno"),
        ("guardian", "Encarregado"),
        ("finance_officer", "Responsável financeiro"),
        ("support", "Suporte"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="school_profile",
        verbose_name="Usuário",
    )
    # Papel do usuário no contexto escolar.
    role = models.CharField(max_length=40, choices=ROLE_CHOICES, verbose_name="Papel")
    # Escola associada (quando aplicável).
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Escola")
    # Escopo geográfico adicional.
    province = models.CharField(max_length=100, blank=True, verbose_name="Província")
    district = models.CharField(max_length=100, blank=True, verbose_name="Distrito")
    # Foto do utilizador (pode ser URL ou data URL inline).
    avatar_url = models.TextField(blank=True, verbose_name="Avatar")
    # Flag de ativação.
    active = models.BooleanField(default=True, verbose_name="Ativo")

    def clean(self):
        """Herda tenant da escola quando informada."""
        school_tenant = (self.school.tenant_id or "").strip() if self.school_id else ""
        if school_tenant:
            if self.tenant_id and self.tenant_id != school_tenant:
                raise ValidationError({"tenant_id": "O tenant do perfil deve coincidir com o tenant da escola."})
            if not self.tenant_id:
                self.tenant_id = school_tenant

    def save(self, *args, **kwargs):
        """Valida antes de salvar."""
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        """Exibe username e papel."""
        return f"{self.user.username} - {self.role}"

    class Meta:
        verbose_name = "Perfil de utilizador"
        verbose_name_plural = "Perfis de utilizador"
        ordering = ["user__username"]
