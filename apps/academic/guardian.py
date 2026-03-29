from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseNamedCodeModel, tenant_id_from_user


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
