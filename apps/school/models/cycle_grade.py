from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseNamedCodeModel


class Cycle(BaseNamedCodeModel):
    CODE_PREFIX = "CYC"
    TRACK_CHOICES = [
        ("general", "Ensino geral"),
        ("technical", "Ensino técnico profissional"),
    ]

    code = models.CharField(max_length=40, unique=True, verbose_name="Código do ciclo")
    track = models.CharField(max_length=20, choices=TRACK_CHOICES, default="general", verbose_name="Trilho")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="Ordem")

    def __str__(self):
        return f"{self.name or self.code} ({self.get_track_display()})"

    class Meta:
        verbose_name = "Ciclo"
        verbose_name_plural = "Ciclos"
        ordering = ["track", "order", "code"]


class Grade(BaseNamedCodeModel):
    CODE_PREFIX = "GRA"

    number = models.PositiveSmallIntegerField(unique=True, verbose_name="Classe")
    cycle = models.PositiveSmallIntegerField(verbose_name="Ciclo")
    cycle_model = models.ForeignKey(
        Cycle,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="grades",
        verbose_name="Ciclo (model)",
    )
    name = models.CharField(max_length=50, blank=True, verbose_name="Nome")

    @staticmethod
    def education_level_for_grade(number: int) -> str:
        return "primario" if number <= 6 else "secundario"

    @staticmethod
    def cycle_for_grade(number: int) -> int:
        if number <= 3 or 7 <= number <= 9:
            return 1
        return 2

    @property
    def education_level(self) -> str:
        return self.education_level_for_grade(self.number)

    def clean(self):
        if not 1 <= self.number <= 12:
            raise ValidationError({"number": "A classe deve estar entre 1 e 12."})
        self.cycle = self.cycle_for_grade(self.number)
        if self.number <= 6 and not self.name:
            self.name = f"Classe {self.number}"
        if self.cycle_model_id is None:
            self.cycle_model = Cycle.objects.filter(code=self._cycle_model_code()).first()

    def _cycle_model_code(self):
        if self.number <= 3:
            return "primary_cycle_1"
        if self.number <= 6:
            return "primary_cycle_2"
        if self.number <= 9:
            return "secondary_cycle_1"
        if self.number <= 12:
            return "secondary_cycle_2"
        return None

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.number}ª"

    class Meta:
        verbose_name = "Classe"
        verbose_name_plural = "Classes"
        ordering = ["number"]
