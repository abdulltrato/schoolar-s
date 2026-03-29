from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseNamedCodeModel


class School(BaseNamedCodeModel):
    CODE_PREFIX = "ESC"

    code = models.CharField(max_length=30, unique=True, verbose_name="Código")
    tenant_id = models.CharField(max_length=50, unique=True, blank=True, verbose_name="Identificador do tenant")
    district = models.CharField(max_length=100, blank=True, verbose_name="Distrito")
    province = models.CharField(max_length=100, blank=True, verbose_name="Província")
    active = models.BooleanField(default=True, verbose_name="Ativa")

    def clean(self):
        self.tenant_id = (self.tenant_id or self.code or "").strip()
        if not self.tenant_id:
            raise ValidationError({"tenant_id": "tenant_id é obrigatório."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Escola"
        verbose_name_plural = "Escolas"
        ordering = ["name"]
