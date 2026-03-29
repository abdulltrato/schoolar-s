from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseCodeModel


class SubjectCurriculumPlan(BaseCodeModel):
    CODE_PREFIX = "SCP"

    grade_subject = models.ForeignKey("school.GradeSubject", on_delete=models.CASCADE, verbose_name="Disciplina da classe")
    objectives = models.TextField(blank=True, verbose_name="Objetivos")
    methodology = models.TextField(blank=True, verbose_name="Metodologia")
    assessment_criteria = models.TextField(blank=True, verbose_name="Critérios de avaliação")
    active = models.BooleanField(default=True, verbose_name="Ativo")
    planned_competencies = models.ManyToManyField("curriculum.Competency", blank=True, verbose_name="Competências planeadas")

    class Meta:
        verbose_name = "Plano curricular"
        verbose_name_plural = "Planos curriculares"

    def clean(self):
        if not self.grade_subject_id:
            raise ValidationError({"grade_subject": "Informe disciplina/classe."})
