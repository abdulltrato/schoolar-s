from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseCodeModel
from .component import AssessmentComponent


class AssessmentOutcomeMap(BaseCodeModel):
    CODE_PREFIX = "AOM"

    component = models.ForeignKey(AssessmentComponent, on_delete=models.CASCADE, verbose_name="Componente")
    outcome = models.ForeignKey("curriculum.LearningOutcome", on_delete=models.CASCADE, verbose_name="Resultado de aprendizagem")
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=100, verbose_name="Peso")
    active = models.BooleanField(default=True, verbose_name="Ativo")

    def clean(self):
        component_tenant = (self.component.tenant_id or "").strip() if self.component_id else ""
        outcome_tenant = (self.outcome.tenant_id or "").strip() if self.outcome_id else ""
        if component_tenant and outcome_tenant and component_tenant != outcome_tenant:
            raise ValidationError({"tenant_id": "Componente e resultado devem pertencer ao mesmo tenant."})
        if self.tenant_id and component_tenant and self.tenant_id != component_tenant:
            raise ValidationError({"tenant_id": "O tenant deve coincidir com o do componente."})
        if outcome_tenant and self.tenant_id and self.tenant_id != outcome_tenant:
            raise ValidationError({"tenant_id": "O tenant deve coincidir com o do resultado."})
        self.tenant_id = self.tenant_id or component_tenant or outcome_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id is required."})
        if self.weight <= 0 or self.weight > 100:
            raise ValidationError({"weight": "O peso deve estar entre 0 e 100."})

        if self.outcome_id and self.component_id:
            subject_id = self.component.grade_subject.subject_id
            grade_id = self.component.grade_subject.grade_id
            outcome_subject = self.outcome.subject_id
            outcome_grade = self.outcome.grade_id
            if outcome_subject and outcome_subject != subject_id:
                raise ValidationError({"outcome": "O resultado deve pertencer à mesma disciplina do componente."})
            if outcome_grade and outcome_grade != grade_id:
                raise ValidationError({"outcome": "O resultado deve pertencer à mesma classe do componente."})
            if self.outcome.cycle and self.component.grade_subject.grade.cycle != self.outcome.cycle:
                raise ValidationError({"outcome": "O resultado deve pertencer ao mesmo ciclo do componente."})

        if self.component_id:
            existing = AssessmentOutcomeMap.objects.filter(component=self.component, active=True).exclude(pk=self.pk)
            total_weight = sum([mapping.weight for mapping in existing])
            if total_weight + self.weight > 100:
                raise ValidationError({"weight": "A soma dos pesos por componente não pode exceder 100."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.component} -> {self.outcome.code}"

    class Meta:
        verbose_name = "Mapeamento componente-resultado"
        verbose_name_plural = "Mapeamentos componente-resultado"
        ordering = ["component__name", "outcome__code"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "component", "outcome"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_assessment_outcome_map_active",
            ),
        ]
