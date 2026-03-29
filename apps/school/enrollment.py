from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseCodeModel


class Enrollment(BaseCodeModel):
    CODE_PREFIX = "ENR"

    student = models.ForeignKey("academic.Student", on_delete=models.CASCADE, verbose_name="Aluno")
    classroom = models.ForeignKey("school.Classroom", on_delete=models.CASCADE, verbose_name="Turma")
    enrollment_date = models.DateField(auto_now_add=True, verbose_name="Data de matrícula")

    class Meta:
        verbose_name = "Matrícula"
        verbose_name_plural = "Matrículas"
        constraints = [
            models.UniqueConstraint(
                fields=["student", "classroom"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_enrollment_active",
            ),
        ]

    def clean(self):
        if self.student_id and self.classroom_id:
            if self.student.grade != self.classroom.grade.number:
                raise ValidationError({"classroom": "Classe do aluno difere da turma."})
