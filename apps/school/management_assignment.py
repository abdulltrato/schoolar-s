from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseCodeModel


class ManagementAssignment(BaseCodeModel):
    CODE_PREFIX = "MAS"
    ROLE_CHOICES = [
        ("director_escola", "Diretor da escola"),
        ("director_adjunto_pedagogico", "Dir. adjunto pedagógico"),
        ("director_ciclo", "Diretor de ciclo"),
        ("coordenador_classe", "Coordenador de classe"),
        ("director_turma", "Diretor de turma"),
    ]

    teacher = models.ForeignKey("school.Teacher", on_delete=models.CASCADE, verbose_name="Professor")
    school = models.ForeignKey("school.School", on_delete=models.CASCADE, verbose_name="Escola")
    academic_year = models.ForeignKey("school.AcademicYear", on_delete=models.CASCADE, verbose_name="Ano letivo")
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, verbose_name="Cargo")
    grade = models.ForeignKey("school.Grade", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Classe")
    classroom = models.ForeignKey("school.Classroom", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Turma")
    cycle = models.IntegerField(null=True, blank=True, verbose_name="Ciclo")
    active = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        verbose_name = "Cargo de gestão"
        verbose_name_plural = "Cargos de gestão"
        constraints = [
            models.UniqueConstraint(
                fields=["teacher", "school", "academic_year", "role"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_management_assignment_active",
            ),
        ]

    def clean(self):
        if self.role == "director_turma" and not self.classroom_id:
            raise ValidationError({"classroom": "Diretor de turma requer turma definida."})
        if self.role == "coordenador_classe" and not self.grade_id:
            raise ValidationError({"grade": "Coordenador de classe requer classe definida."})
