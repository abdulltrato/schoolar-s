from django.db import models

from core.models import BaseNamedCodeModel


class CurriculumArea(BaseNamedCodeModel):
    CODE_PREFIX = "CRA"

    class Meta:
        verbose_name = "Área curricular"
        verbose_name_plural = "Áreas curriculares"
        ordering = ["name"]
