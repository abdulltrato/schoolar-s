from django.db import models

from core.models import BaseNamedCodeModel
from .area import CurriculumArea


class Subject(BaseNamedCodeModel):
    CODE_PREFIX = "SUB"

    area = models.ForeignKey(CurriculumArea, on_delete=models.CASCADE, verbose_name="Área")
    cycle = models.IntegerField(verbose_name="Ciclo")

    class Meta:
        verbose_name = "Disciplina"
        verbose_name_plural = "Disciplinas"
        ordering = ["name"]


class SubjectSpecialty(BaseNamedCodeModel):
    CODE_PREFIX = "SPS"

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name="Disciplina")

    class Meta:
        verbose_name = "Especialidade por disciplina"
        verbose_name_plural = "Especialidades por disciplina"
        ordering = ["name"]
