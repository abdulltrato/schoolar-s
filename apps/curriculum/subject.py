from django.db import models
# Campos e relacionamentos do ORM.

from core.models import BaseNamedCodeModel
# Modelo base com nome, código e auditoria.
from .area import CurriculumArea
# Área curricular associada à disciplina.


class Subject(BaseNamedCodeModel):
    """Disciplina pertencente a uma área curricular e ciclo."""

    # Prefixo usado para gerar código.
    CODE_PREFIX = "SUB"

    # Área curricular vinculada.
    area = models.ForeignKey(CurriculumArea, on_delete=models.CASCADE, verbose_name="Área")
    # Ciclo (1 ou 2).
    cycle = models.IntegerField(verbose_name="Ciclo")

    class Meta:
        # Rótulo singular.
        verbose_name = "Disciplina"
        # Rótulo plural.
        verbose_name_plural = "Disciplinas"
        # Ordena alfabeticamente.
        ordering = ["name"]


class SubjectSpecialty(BaseNamedCodeModel):
    """Especialidade específica dentro de uma disciplina."""

    # Prefixo para geração automática de código.
    CODE_PREFIX = "SPS"

    # Disciplina a que a especialidade pertence.
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name="Disciplina")

    class Meta:
        # Rótulo singular.
        verbose_name = "Especialidade por disciplina"
        # Rótulo plural.
        verbose_name_plural = "Especialidades por disciplina"
        # Ordenação padrão por nome.
        ordering = ["name"]
