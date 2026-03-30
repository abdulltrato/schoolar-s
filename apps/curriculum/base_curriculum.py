from django.db import models
# Componentes de modelagem do Django.

from core.models import BaseCodeModel
# Modelo base com código, auditoria e soft-delete.


class BaseCurriculum(BaseCodeModel):
    """Currículo genérico que lista competências por ciclo."""

    # Prefixo de código para geração automática.
    CODE_PREFIX = "BCR"

    # Ciclo a que o currículo pertence (ex.: 1 ou 2).
    cycle = models.IntegerField(verbose_name="Ciclo")
    # IDs das competências que compõem o currículo.
    competency_ids = models.JSONField(default=list, blank=True, verbose_name="Competências base (IDs)")

    class Meta:
        # Nome singular no admin.
        verbose_name = "Currículo base"
        # Nome plural no admin.
        verbose_name_plural = "Currículos base"
