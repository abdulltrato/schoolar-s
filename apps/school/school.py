from django.db import models

from core.models import BaseNamedCodeModel


class School(BaseNamedCodeModel):
    CODE_PREFIX = "SCH"

    district = models.CharField(max_length=100, blank=True, verbose_name="Distrito")
    province = models.CharField(max_length=100, blank=True, verbose_name="Província")
    active = models.BooleanField(default=True, verbose_name="Ativa")

    class Meta:
        verbose_name = "Escola"
        verbose_name_plural = "Escolas"
