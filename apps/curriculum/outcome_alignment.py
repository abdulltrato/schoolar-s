from django.db import models
# Campos do ORM do Django.

from core.models import BaseCodeModel
# Modelo base que provê código e auditoria.


class CompetencyOutcome(BaseCodeModel):
    """Ligação entre uma competência e um resultado de aprendizagem, com peso."""

    # Prefixo para geração de código.
    CODE_PREFIX = "COT"

    # Competência mapeada.
    competency = models.ForeignKey("curriculum.Competency", on_delete=models.CASCADE, verbose_name="Competência")
    # Resultado de aprendizagem vinculado.
    outcome = models.ForeignKey("curriculum.LearningOutcome", on_delete=models.CASCADE, verbose_name="Resultado de aprendizagem")
    # Peso relativo do alinhamento.
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=100, verbose_name="Peso")

    class Meta:
        # Rótulo singular.
        verbose_name = "Mapeamento competência-resultado"
        # Rótulo plural.
        verbose_name_plural = "Mapeamentos competência-resultado"
        # Ordenação por nome da competência e código do resultado.
        ordering = ["competency__name", "outcome__code"]
