from django.core.exceptions import ValidationError
# Exceção padrão de validação.
from django.db import models
# Campos e relacionamentos do ORM.

from core.models import BaseCodeModel
# Modelo base com código e auditoria.


class SubjectCurriculumPlan(BaseCodeModel):
    """Plano curricular para uma disciplina em uma classe específica."""

    # Prefixo para geração de código.
    CODE_PREFIX = "SCP"

    # Relação com disciplina-classe oferecida.
    grade_subject = models.ForeignKey("school.GradeSubject", on_delete=models.CASCADE, verbose_name="Disciplina da classe")
    # Objetivos gerais do plano.
    objectives = models.TextField(blank=True, verbose_name="Objetivos")
    # Estratégias/metodologia de ensino.
    methodology = models.TextField(blank=True, verbose_name="Metodologia")
    # Critérios e pesos de avaliação.
    assessment_criteria = models.TextField(blank=True, verbose_name="Critérios de avaliação")
    # Flag de ativação do plano.
    active = models.BooleanField(default=True, verbose_name="Ativo")
    # Competências planejadas para a disciplina.
    planned_competencies = models.ManyToManyField("curriculum.Competency", blank=True, verbose_name="Competências planeadas")

    class Meta:
        # Rótulo singular.
        verbose_name = "Plano curricular"
        # Rótulo plural.
        verbose_name_plural = "Planos curriculares"

    def clean(self):
        """Valida obrigatoriedade da disciplina da classe."""
        # Exige vínculo com uma disciplina/classe.
        if not self.grade_subject_id:
            raise ValidationError({"grade_subject": "Informe disciplina/classe."})
