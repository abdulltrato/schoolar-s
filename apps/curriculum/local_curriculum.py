from django.db import models
# Componentes do ORM.

from core.models import BaseCodeModel
# Modelo base com código e auditoria.


class LocalCurriculum(BaseCodeModel):
    """Currículo específico de um tenant, com lista de competências locais."""

    # Prefixo usado para gerar código automático.
    CODE_PREFIX = "LCR"

    # Identificador do tenant proprietário do currículo.
    tenant_id = models.CharField(max_length=100, verbose_name="Tenant")
    # Ciclo a que o currículo pertence.
    cycle = models.IntegerField(verbose_name="Ciclo")
    # IDs das competências locais vinculadas.
    competency_ids = models.JSONField(default=list, blank=True, verbose_name="Competências locais (IDs)")

    class Meta:
        # Nome singular no admin.
        verbose_name = "Currículo local"
        # Nome plural no admin.
        verbose_name_plural = "Currículos locais"
