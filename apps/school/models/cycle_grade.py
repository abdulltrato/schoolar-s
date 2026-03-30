from django.core.exceptions import ValidationError
# Exceção de validação.
from django.db import models
# Campos e utilitários do ORM.

from core.models import BaseNamedCodeModel
# Modelo base com nome, código e auditoria.


class Cycle(BaseNamedCodeModel):
    """Ciclo de ensino (geral ou técnico) com ordenação."""

    CODE_PREFIX = "CYC"
    TRACK_CHOICES = [
        ("general", "Ensino geral"),
        ("technical", "Ensino técnico profissional"),
    ]

    # Código único para referência.
    code = models.CharField(max_length=40, unique=True, verbose_name="Código do ciclo")
    # Trilho (geral/técnico).
    track = models.CharField(max_length=20, choices=TRACK_CHOICES, default="general", verbose_name="Trilho")
    # Ordem de exibição.
    order = models.PositiveSmallIntegerField(default=0, verbose_name="Ordem")

    def __str__(self):
        return f"{self.name or self.code} ({self.get_track_display()})"

    class Meta:
        verbose_name = "Ciclo"
        verbose_name_plural = "Ciclos"
        ordering = ["track", "order", "code"]


class Grade(BaseNamedCodeModel):
    """Classe/ano escolar com derivação automática de ciclo e nome."""

    CODE_PREFIX = "GRA"

    # Número da classe (ex.: 1..12).
    number = models.PositiveSmallIntegerField(unique=True, verbose_name="Classe")
    # Ciclo (1 ou 2) derivado do número.
    cycle = models.PositiveSmallIntegerField(verbose_name="Ciclo")
    # Modelo de ciclo (legado) opcional.
    cycle_model = models.ForeignKey(
        Cycle,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="grades",
        verbose_name="Ciclo (model)",
    )
    # Nome amigável (pode ser preenchido automaticamente).
    name = models.CharField(max_length=50, blank=True, verbose_name="Nome")

    @staticmethod
    def education_level_for_grade(number: int) -> str:
        """Retorna nível educacional (primário/secundário) para o número da classe."""
        return "primario" if number <= 6 else "secundario"

    @staticmethod
    def cycle_for_grade(number: int) -> int:
        """Determina ciclo (1 ou 2) conforme número da classe."""
        if number <= 3 or 7 <= number <= 9:
            return 1
        return 2

    @property
    def education_level(self) -> str:
        return self.education_level_for_grade(self.number)

    def clean(self):
        """Valida faixa do número, preenche ciclo, nome e ciclo_model default."""
        if not 1 <= self.number <= 12:
            raise ValidationError({"number": "A classe deve estar entre 1 e 12."})
        self.cycle = self.cycle_for_grade(self.number)
        if self.number <= 6 and not self.name:
            self.name = f"Classe {self.number}"
        if self.cycle_model_id is None:
            self.cycle_model = Cycle.objects.filter(code=self._cycle_model_code()).first()

    def _cycle_model_code(self):
        """Mapeia número de classe para código do modelo de ciclo."""
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
        """Valida antes de salvar."""
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        """Representa classe como 'Nª'."""
        return f"{self.number}ª"

    class Meta:
        verbose_name = "Classe"
        verbose_name_plural = "Classes"
        ordering = ["number"]
