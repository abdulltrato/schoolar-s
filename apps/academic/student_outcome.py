from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseCodeModel
from .student import Student


# Modelo que armazena o nível de domínio de um aluno em um resultado de aprendizagem.
class StudentOutcome(BaseCodeModel):
    """Domínio do aluno sobre um resultado de aprendizagem, com status derivado e recálculo por avaliações."""
    # Prefixo para códigos automáticos.
    CODE_PREFIX = "STO"
    # Opções de status textual associadas ao nível numérico.
    MASTERY_CHOICES = [
        ("not_started", "Não iniciado"),
        ("developing", "Em desenvolvimento"),
        ("proficient", "Proficiente"),
        ("advanced", "Avançado"),
    ]

    # FK para o aluno.
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="Aluno")
    # FK para o resultado de aprendizagem.
    outcome = models.ForeignKey("curriculum.LearningOutcome", on_delete=models.CASCADE, verbose_name="Resultado de aprendizagem")
    # Nível numérico de domínio (0.0 a 5.0).
    mastery_level = models.DecimalField(max_digits=3, decimal_places=1, default=0.0, verbose_name="Nível")
    # Status textual derivado do nível.
    status = models.CharField(max_length=20, choices=MASTERY_CHOICES, default="not_started", verbose_name="Estado")
    # Contagem de evidências usadas no cálculo.
    evidence_count = models.PositiveIntegerField(default=0, verbose_name="Evidências")

    def clean(self):
        # Obtém tenant do aluno se informado.
        student_tenant = (self.student.tenant_id or "").strip() if self.student_id else ""
        # Obtém tenant do resultado se informado.
        outcome_tenant = (self.outcome.tenant_id or "").strip() if self.outcome_id else ""
        # Exige que aluno e resultado pertençam ao mesmo tenant.
        if student_tenant and outcome_tenant and student_tenant != outcome_tenant:
            raise ValidationError({"tenant_id": "Aluno e resultado devem pertencer ao mesmo tenant."})
        # Valida coerência entre tenant da instância e o do aluno.
        if self.tenant_id and student_tenant and self.tenant_id != student_tenant:
            raise ValidationError({"tenant_id": "O tenant deve coincidir com o do aluno."})
        # Valida coerência entre tenant da instância e o do resultado.
        if outcome_tenant and self.tenant_id and self.tenant_id != outcome_tenant:
            raise ValidationError({"tenant_id": "O tenant deve coincidir com o do resultado."})
        # Preenche tenant com o valor disponível.
        self.tenant_id = self.tenant_id or student_tenant or outcome_tenant
        # Exige tenant no final.
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id é obrigatório. Envie o header X-Tenant-ID ou configure tenant_id no seu perfil (UserProfile)."})
        # Valida faixa permitida do nível.
        if not 0 <= self.mastery_level <= 5:
            raise ValidationError({"mastery_level": "O nível deve estar entre 0.0 e 5.0."})

    @staticmethod
    def _status_for_mastery(level: Decimal) -> str:
        # Traduz nível numérico para status textual.
        if level >= Decimal("4.5"):
            return "advanced"
        if level >= Decimal("3.0"):
            return "proficient"
        if level >= Decimal("1.0"):
            return "developing"
        return "not_started"

    @classmethod
    def recalculate_for_components(cls, *, student, component_ids):
        # Remove ids vazios/None.
        component_ids = [component_id for component_id in component_ids if component_id]
        # Se não há componentes, não há o que recalcular.
        if not component_ids:
            return
        # Importa aqui para evitar import circular.
        from apps.assessment.models import AssessmentOutcomeMap

        # Busca outcomes mapeados para os componentes informados.
        outcome_ids = list(
            AssessmentOutcomeMap.objects.filter(component_id__in=component_ids, active=True)
            .values_list("outcome_id", flat=True)
            .distinct()
        )
        # Se há outcomes, delega ao método principal.
        if outcome_ids:
            cls.recalculate_for_outcomes(student=student, outcome_ids=outcome_ids)

    @classmethod
    def recalculate_for_outcomes(cls, *, student, outcome_ids):
        # Se nenhuma lista foi passada, encerra.
        if not outcome_ids:
            return
        # Importa modelos necessários para cálculo.
        from apps.assessment.models import Assessment, AssessmentOutcomeMap

        # Carrega mapeamentos outcome->component com os pesos.
        mappings = list(
            AssessmentOutcomeMap.objects.filter(outcome_id__in=outcome_ids, active=True).select_related("component")
        )
        # Sem mapeamentos não há o que recalcular.
        if not mappings:
            return

        # Dicionário outcome_id -> {component_id: peso}.
        outcome_components: dict[int, dict[int, Decimal]] = {}
        # Conjunto de componentes envolvidos.
        component_ids = set()
        for mapping in mappings:
            outcome_components.setdefault(mapping.outcome_id, {})[mapping.component_id] = Decimal(mapping.weight)
            component_ids.add(mapping.component_id)

        # Busca avaliações do aluno nos componentes relevantes.
        assessments = Assessment.objects.filter(
            student=student,
            component_id__in=component_ids,
            score__isnull=False,
        ).select_related("component")

        # Agrupa avaliações por componente.
        assessments_by_component: dict[int, list] = {}
        for assessment in assessments:
            assessments_by_component.setdefault(assessment.component_id, []).append(assessment)

        # Recalcula cada resultado.
        for outcome_id, component_weights in outcome_components.items():
            # Acumuladores para média ponderada.
            total_weight = Decimal("0")
            weighted_total = Decimal("0")
            evidence_count = 0

            # Percorre componentes mapeados.
            for component_id, weight in component_weights.items():
                # Ignora pesos não positivos.
                if weight <= 0:
                    continue
                # Usa cada avaliação encontrada para o componente.
                for assessment in assessments_by_component.get(component_id, []):
                    # Nota máxima da componente.
                    max_score = Decimal(assessment.component.max_score)
                    if max_score <= 0:
                        continue
                    # Nota obtida pelo aluno.
                    score = Decimal(assessment.score)
                    # Normaliza para escala de 0 a 20.
                    normalized = (score / max_score) * Decimal("20")
                    # Soma valor ponderado.
                    weighted_total += normalized * weight
                    # Soma pesos totais.
                    total_weight += weight
                    # Incrementa contador de evidências.
                    evidence_count += 1

            # Se não há peso acumulado, zera o registro.
            if total_weight <= 0:
                cls.all_objects.filter(student=student, outcome_id=outcome_id).update(
                    mastery_level=Decimal("0.0"),
                    status="not_started",
                    evidence_count=0,
                    deleted_at=None,
                )
                continue

            # Calcula média ponderada.
            average = weighted_total / total_weight
            # Converte média (0-20) para escala de domínio (0-5).
            mastery = (average / Decimal("20")) * Decimal("5")
            # Arredonda para uma casa decimal.
            mastery = mastery.quantize(Decimal("0.1"))
            # Determina status textual correspondente.
            status = cls._status_for_mastery(mastery)
            # Recupera tenant do aluno.
            tenant_id = (student.tenant_id or "").strip()

            # Atualiza ou cria registro ativo com os novos valores.
            cls.all_objects.update_or_create(
                student=student,
                outcome_id=outcome_id,
                defaults={
                    "tenant_id": tenant_id,
                    "mastery_level": mastery,
                    "status": status,
                    "evidence_count": evidence_count,
                    "deleted_at": None,
                },
            )

    def save(self, *args, **kwargs):
        # Valida antes de salvar.
        self.full_clean()
        # Persiste com comportamento padrão.
        return super().save(*args, **kwargs)

    def __str__(self):
        # Exibe aluno e código do resultado para identificação.
        return f"{self.student} - {self.outcome.code}"

    class Meta:
        # Garante unicidade do resultado por aluno e tenant enquanto ativo.
        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "student", "outcome"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_student_outcome_active",
            ),
        ]
        # Metadados de exibição.
        verbose_name = "Resultado do aluno"
        verbose_name_plural = "Resultados do aluno"
        # Ordena registros mais recentes primeiro.
        ordering = ["-updated_at"]
