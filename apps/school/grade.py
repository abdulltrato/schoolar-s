from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseNamedCodeModel
from .cycle import Cycle


class Grade(BaseNamedCodeModel):
    CODE_PREFIX = "GRD"

    number = models.IntegerField(verbose_name="Classe")
    cycle = models.IntegerField(verbose_name="Ciclo")
    cycle_model = models.ForeignKey(Cycle, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Modelo de ciclo")

    class Meta:
        verbose_name = "Classe"
        verbose_name_plural = "Classes"
        ordering = ["number"]

    @property
    def education_level(self) -> str:
        if self.number is None:
            return ""
        return "primario" if self.number <= 6 else "secundario"

    def clean(self):
        if self.number is None or self.number < 1:
            raise ValidationError({"number": "Número da classe inválido."})


class GradeSubject(models.Model):
    academic_year = models.ForeignKey("school.AcademicYear", on_delete=models.CASCADE, verbose_name="Ano letivo")
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, verbose_name="Classe")
    subject = models.ForeignKey("curriculum.Subject", on_delete=models.CASCADE, verbose_name="Disciplina")
    weekly_workload = models.PositiveSmallIntegerField(default=3, verbose_name="Carga horária semanal")

    class Meta:
        verbose_name = "Disciplina da classe"
        verbose_name_plural = "Disciplinas da classe"
        constraints = [
            models.UniqueConstraint(
                fields=["academic_year", "grade", "subject"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_grade_subject_active",
            ),
        ]
