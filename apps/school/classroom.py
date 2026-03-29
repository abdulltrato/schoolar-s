from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseCodeModel
from .grade import Grade
from .teacher import Teacher
from .school import School
from .academic_year import AcademicYear


class Classroom(BaseCodeModel):
    CODE_PREFIX = "CLR"

    name = models.CharField(max_length=50, verbose_name="Nome")
    school = models.ForeignKey(School, on_delete=models.CASCADE, verbose_name="Escola")
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, verbose_name="Classe")
    cycle = models.IntegerField(verbose_name="Ciclo")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, verbose_name="Ano letivo")
    lead_teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name="classrooms", verbose_name="Professor diretor")
    cycle_model = models.ForeignKey("school.Cycle", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Modelo de ciclo")

    class Meta:
        verbose_name = "Turma"
        verbose_name_plural = "Turmas"
        constraints = [
            models.UniqueConstraint(
                fields=["academic_year", "name", "school"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_classroom_year_name_school",
            ),
        ]

    def clean(self):
        if self.grade and self.cycle and self.grade.cycle != self.cycle:
            raise ValidationError({"grade": "A turma deve seguir o mesmo ciclo da classe."})
