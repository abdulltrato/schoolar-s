from django.db import models

from core.models import BaseNamedCodeModel
from .school import School


class Teacher(BaseNamedCodeModel):
    CODE_PREFIX = "TCH"
    user = models.OneToOneField("auth.User", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuário")
    school = models.ForeignKey(School, on_delete=models.CASCADE, verbose_name="Escola")
    specialty = models.ForeignKey("curriculum.SubjectSpecialty", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Especialidade")

    class Meta:
        verbose_name = "Professor"
        verbose_name_plural = "Professores"
        ordering = ["name"]


class TeacherSpecialty(BaseNamedCodeModel):
    CODE_PREFIX = "TSP"
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="Professor")

    class Meta:
        verbose_name = "Especialidade de professor"
        verbose_name_plural = "Especialidades de professor"
