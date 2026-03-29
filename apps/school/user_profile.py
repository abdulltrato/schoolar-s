from django.db import models

from core.models import BaseCodeModel


class UserProfile(BaseCodeModel):
    CODE_PREFIX = "SUP"
    ROLE_CHOICES = [
        ("national_admin", "Administrador nacional"),
        ("provincial_admin", "Administrador provincial"),
        ("district_admin", "Administrador distrital"),
        ("school_director", "Diretor da escola"),
        ("teacher", "Professor"),
        ("student", "Aluno"),
        ("guardian", "Encarregado"),
    ]

    user = models.OneToOneField("auth.User", on_delete=models.CASCADE, related_name="school_profile", verbose_name="Usuário")
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default="national_admin", verbose_name="Papel")
    school = models.ForeignKey("school.School", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Escola")
    province = models.CharField(max_length=100, blank=True, verbose_name="Província")
    district = models.CharField(max_length=100, blank=True, verbose_name="Distrito")
    active = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        verbose_name = "Perfil de usuário"
        verbose_name_plural = "Perfis de usuário"
