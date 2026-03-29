from django.db import models

from core.models import BaseCodeModel


class LocalCurriculum(BaseCodeModel):
    CODE_PREFIX = "LCR"

    tenant_id = models.CharField(max_length=100, verbose_name="Tenant")
    cycle = models.IntegerField(verbose_name="Ciclo")
    competency_ids = models.JSONField(default=list, blank=True, verbose_name="Competências locais (IDs)")

    class Meta:
        verbose_name = "Currículo local"
        verbose_name_plural = "Currículos locais"
