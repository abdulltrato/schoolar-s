from django.core.exceptions import ValidationError
# Exceção de validação.
from django.db import models
# Campos do ORM.

from core.models import BaseNamedCodeModel
# Modelo base com nome, código e auditoria.


class School(BaseNamedCodeModel):
    """Escola (tenant) com código próprio e dados de localização."""

    CODE_PREFIX = "ESC"

    # Código da escola (pode coincidir com tenant).
    code = models.CharField(max_length=30, unique=True, verbose_name="Código")
    # Identificador de tenant (preenchido com code se vazio).
    tenant_id = models.CharField(max_length=50, unique=True, blank=True, verbose_name="Identificador do tenant")
    # Localização.
    district = models.CharField(max_length=100, blank=True, verbose_name="Distrito")
    province = models.CharField(max_length=100, blank=True, verbose_name="Província")
    # Ativa/inativa.
    active = models.BooleanField(default=True, verbose_name="Ativa")

    def clean(self):
        """Garante tenant_id preenchido (code como fallback)."""
        self.tenant_id = (self.tenant_id or self.code or "").strip()
        if not self.tenant_id:
            raise ValidationError({"tenant_id": "tenant_id é obrigatório."})

    def save(self, *args, **kwargs):
        """Valida antes de persistir."""
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        """Retorna nome da escola."""
        return self.name

    class Meta:
        verbose_name = "Escola"
        verbose_name_plural = "Escolas"
        ordering = ["name"]
