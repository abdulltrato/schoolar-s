from django.db import models

from core.models import BaseCodeModel


class CompetencyOutcome(BaseCodeModel):
    CODE_PREFIX = "COT"

    competency = models.ForeignKey("curriculum.Competency", on_delete=models.CASCADE, verbose_name="Competência")
    outcome = models.ForeignKey("curriculum.LearningOutcome", on_delete=models.CASCADE, verbose_name="Resultado de aprendizagem")
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=100, verbose_name="Peso")

    class Meta:
        verbose_name = "Mapeamento competência-resultado"
        verbose_name_plural = "Mapeamentos competência-resultado"
        ordering = ["competency__name", "outcome__code"]
