from django.core.exceptions import ValidationError
# Importa exceção usada para validar regras de domínio.
from django.db import models
# Importa classes base do ORM.

from core.models import BaseCodeModel
# Modelo base que provê código e campos auditáveis.
from .component import AssessmentComponent
# Modelo de componente avaliativo usado na FK.


class AssessmentOutcomeMap(BaseCodeModel):
    """Relaciona um componente avaliativo a um resultado de aprendizagem com peso relativo."""

    # Prefixo usado na geração de código automático.
    CODE_PREFIX = "AOM"

    # Componente avaliativo associado ao resultado.
    component = models.ForeignKey(AssessmentComponent, on_delete=models.CASCADE, verbose_name="Componente")
    # Resultado de aprendizagem mapeado.
    outcome = models.ForeignKey("curriculum.LearningOutcome", on_delete=models.CASCADE, verbose_name="Resultado de aprendizagem")
    # Peso percentual do resultado dentro do componente.
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=100, verbose_name="Peso")
    # Indicador de ativo para controle lógico.
    active = models.BooleanField(default=True, verbose_name="Ativo")

    def clean(self):
        # Captura tenants dos relacionados para validar consistência.
        component_tenant = (self.component.tenant_id or "").strip() if self.component_id else ""
        outcome_tenant = (self.outcome.tenant_id or "").strip() if self.outcome_id else ""
        # Garante que componente e resultado compartilhem o mesmo tenant.
        if component_tenant and outcome_tenant and component_tenant != outcome_tenant:
            raise ValidationError({"tenant_id": "Componente e resultado devem pertencer ao mesmo tenant."})
        # Confirma que tenant do registro combina com o do componente.
        if self.tenant_id and component_tenant and self.tenant_id != component_tenant:
            raise ValidationError({"tenant_id": "O tenant deve coincidir com o do componente."})
        # Confirma que tenant do registro combina com o do resultado.
        if outcome_tenant and self.tenant_id and self.tenant_id != outcome_tenant:
            raise ValidationError({"tenant_id": "O tenant deve coincidir com o do resultado."})
        # Preenche tenant herdado quando não informado.
        self.tenant_id = self.tenant_id or component_tenant or outcome_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id is required."})
        # Peso precisa ficar entre 0 e 100.
        if self.weight <= 0 or self.weight > 100:
            raise ValidationError({"weight": "O peso deve estar entre 0 e 100."})

        # Valida alinhamento de disciplina/classe/ciclo entre resultado e componente.
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

        # Evita ultrapassar 100% de peso acumulado por componente ativo.
        if self.component_id:
            existing = AssessmentOutcomeMap.objects.filter(component=self.component, active=True).exclude(pk=self.pk)
            total_weight = sum([mapping.weight for mapping in existing])
            if total_weight + self.weight > 100:
                raise ValidationError({"weight": "A soma dos pesos por componente não pode exceder 100."})

    def save(self, *args, **kwargs):
        # Executa validações antes de salvar.
        self.full_clean()
        # Persiste registro.
        return super().save(*args, **kwargs)

    def __str__(self):
        # Representação curta para admin/listagens.
        return f"{self.component} -> {self.outcome.code}"

    class Meta:
        # Rótulos amigáveis.
        verbose_name = "Mapeamento componente-resultado"
        verbose_name_plural = "Mapeamentos componente-resultado"
        # Ordenação padrão.
        ordering = ["component__name", "outcome__code"]
        # Garante unicidade ativa de componente + resultado por tenant.
        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "component", "outcome"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_assessment_outcome_map_active",
            ),
        ]
