from django.db import models

from core.models import BaseNamedCodeModel


class Cycle(BaseNamedCodeModel):
    CODE_PREFIX = "CYC"

    TRACK_CHOICES = [
        ("primary", "Primário"),
        ("secondary", "Secundário"),
        ("technical", "Técnico"),
    ]

    track = models.CharField(max_length=20, choices=TRACK_CHOICES, default="primary", verbose_name="Trilho")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="Ordem")

    class Meta:
        verbose_name = "Ciclo"
        verbose_name_plural = "Ciclos"
        ordering = ["order"]
