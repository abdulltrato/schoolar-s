from django.db import models

from core.models import BaseCodeModel


class BaseCurriculum(BaseCodeModel):
    CODE_PREFIX = "BCR"

    cycle = models.IntegerField(verbose_name="Ciclo")
    competency_ids = models.JSONField(default=list, blank=True, verbose_name="Competências base (IDs)")

    class Meta:
        verbose_name = "Currículo base"
        verbose_name_plural = "Currículos base"
