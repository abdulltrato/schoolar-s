from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseCodeModel


class TeachingAssignment(BaseCodeModel):
    CODE_PREFIX = "TAS"

    teacher = models.ForeignKey("school.Teacher", on_delete=models.CASCADE, verbose_name="Professor")
    classroom = models.ForeignKey("school.Classroom", on_delete=models.CASCADE, verbose_name="Turma")
    grade_subject = models.ForeignKey("school.GradeSubject", on_delete=models.CASCADE, verbose_name="Disciplina da classe")

    class Meta:
        verbose_name = "Alocação docente"
        verbose_name_plural = "Alocações docentes"
        constraints = [
            models.UniqueConstraint(
                fields=["teacher", "classroom", "grade_subject"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_teaching_assignment_active",
            ),
        ]

    def clean(self):
        if self.grade_subject_id and self.classroom_id:
            if self.grade_subject.academic_year_id != self.classroom.academic_year_id:
                raise ValidationError({"grade_subject": "Disciplina e turma devem ser do mesmo ano letivo."})
            if self.grade_subject.grade_id != self.classroom.grade_id:
                raise ValidationError({"grade_subject": "Disciplina e turma devem ser da mesma classe."})
