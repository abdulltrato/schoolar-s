from django.db import models
# Tipos de campos do ORM do Django.

from core.models import BaseNamedCodeModel
# Modelo base com nome, código e auditoria.


class CurriculumArea(BaseNamedCodeModel):
    """Área curricular que agrupa disciplinas e competências."""

    # Prefixo usado na geração automática de códigos.
    CODE_PREFIX = "CRA"

    class Meta:
        # Rótulo singular exibido no admin.
        verbose_name = "Área curricular"
        # Rótulo plural exibido no admin.
        verbose_name_plural = "Áreas curriculares"
        # Ordena alfabeticamente por nome.
        ordering = ["name"]
