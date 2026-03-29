from django.db import models

from core.models import BaseNamedCodeModel
from .subject import Subject


class Competency(BaseNamedCodeModel):
    CODE_PREFIX = "CPT"

    area = models.CharField(max_length=100, default="general", verbose_name="Área (tag legacy)")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name="Disciplina")
    cycle = models.IntegerField(verbose_name="Ciclo")
    grade = models.IntegerField(null=True, blank=True, verbose_name="Classe")
    active = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        verbose_name = "Competência"
        verbose_name_plural = "Competências"
        ordering = ["name"]
