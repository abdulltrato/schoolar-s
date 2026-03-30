from django.db import models
# Campos e relacionamentos do ORM.

from core.models import BaseNamedCodeModel
# Modelo base com código, nome e auditoria.
from .subject import Subject
# Modelo de disciplina associado à competência.


class Competency(BaseNamedCodeModel):
    """Competência vinculada a uma disciplina e ciclo escolar."""

    # Prefixo para geração automática de código.
    CODE_PREFIX = "CPT"

    # Tag legado de área de conhecimento.
    area = models.CharField(max_length=100, default="general", verbose_name="Área (tag legacy)")
    # Disciplina à qual a competência pertence.
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name="Disciplina")
    # Ciclo (1º ou 2º).
    cycle = models.IntegerField(verbose_name="Ciclo")
    # Classe/ano específico, quando aplicável.
    grade = models.IntegerField(null=True, blank=True, verbose_name="Classe")
    # Flag de ativação.
    active = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        # Rótulos administrativos.
        verbose_name = "Competência"
        verbose_name_plural = "Competências"
        # Ordenação alfabética.
        ordering = ["name"]
