from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseCodeModel
from .student import Student


class StudentOutcome(BaseCodeModel):
    CODE_PREFIX = "STO"
    MASTERY_CHOICES = [
        ("not_started", "Não iniciado"),
        ("developing", "Em desenvolvimento"),
        ("proficient", "Proficiente"),
        ("advanced", "Avançado"),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="Aluno")
    outcome = models.ForeignKey("curriculum.LearningOutcome", on_delete=models.CASCADE, verbose_name="Resultado de aprendizagem")
    mastery_level = models.DecimalField(max_digits=3, decimal_places=1, default=0.0, verbose_name="Nível")
    status = models.CharField(max_length=20, choices=MASTERY_CHOICES, default="not_started", verbose_name="Estado")
    evidence_count = models.PositiveIntegerField(default=0, verbose_name="Evidências")

    def clean(self):
        student_tenant = (self.student.tenant_id or "").strip() if self.student_id else ""
        outcome_tenant = (self.outcome.tenant_id or "").strip() if self.outcome_id else ""
        if student_tenant and outcome_tenant and student_tenant != outcome_tenant:
            raise ValidationError({"tenant_id": "Aluno e resultado devem pertencer ao mesmo tenant."})
        if self.tenant_id and student_tenant and self.tenant_id != student_tenant:
            raise ValidationError({"tenant_id": "O tenant deve coincidir com o do aluno."})
        if outcome_tenant and self.tenant_id and self.tenant_id != outcome_tenant:
            raise ValidationError({"tenant_id": "O tenant deve coincidir com o do resultado."})
        self.tenant_id = self.tenant_id or student_tenant or outcome_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id é obrigatório. Envie o header X-Tenant-ID ou configure tenant_id no seu perfil (UserProfile)."})
        if not 0 <= self.mastery_level <= 5:
            raise ValidationError({"mastery_level": "O nível deve estar entre 0.0 e 5.0."})

    @staticmethod
    def _status_for_mastery(level: Decimal) -> str:
        if level >= Decimal("4.5"):
            return "advanced"
        if level >= Decimal("3.0"):
            return "proficient"
        if level >= Decimal("1.0"):
            return "developing"
        return "not_started"

    @classmethod
    def recalculate_for_components(cls, *, student, component_ids):
        component_ids = [component_id for component_id in component_ids if component_id]
        if not component_ids:
            return
        from apps.assessment.models import AssessmentOutcomeMap

        outcome_ids = list(
            AssessmentOutcomeMap.objects.filter(component_id__in=component_ids, active=True)
            .values_list("outcome_id", flat=True)
            .distinct()
        )
        if outcome_ids:
            cls.recalculate_for_outcomes(student=student, outcome_ids=outcome_ids)

    @classmethod
    def recalculate_for_outcomes(cls, *, student, outcome_ids):
        if not outcome_ids:
            return
        from apps.assessment.models import Assessment, AssessmentOutcomeMap

        mappings = list(
            AssessmentOutcomeMap.objects.filter(outcome_id__in=outcome_ids, active=True).select_related("component")
        )
        if not mappings:
            return

        outcome_components: dict[int, dict[int, Decimal]] = {}
        component_ids = set()
        for mapping in mappings:
            outcome_components.setdefault(mapping.outcome_id, {})[mapping.component_id] = Decimal(mapping.weight)
            component_ids.add(mapping.component_id)

        assessments = Assessment.objects.filter(
            student=student,
            component_id__in=component_ids,
            score__isnull=False,
        ).select_related("component")

        assessments_by_component: dict[int, list] = {}
        for assessment in assessments:
            assessments_by_component.setdefault(assessment.component_id, []).append(assessment)

        for outcome_id, component_weights in outcome_components.items():
            total_weight = Decimal("0")
            weighted_total = Decimal("0")
            evidence_count = 0

            for component_id, weight in component_weights.items():
                if weight <= 0:
                    continue
                for assessment in assessments_by_component.get(component_id, []):
                    max_score = Decimal(assessment.component.max_score)
                    if max_score <= 0:
                        continue
                    score = Decimal(assessment.score)
                    normalized = (score / max_score) * Decimal("20")
                    weighted_total += normalized * weight
                    total_weight += weight
                    evidence_count += 1

            if total_weight <= 0:
                cls.all_objects.filter(student=student, outcome_id=outcome_id).update(
                    mastery_level=Decimal("0.0"),
                    status="not_started",
                    evidence_count=0,
                    deleted_at=None,
                )
                continue

            average = weighted_total / total_weight
            mastery = (average / Decimal("20")) * Decimal("5")
            mastery = mastery.quantize(Decimal("0.1"))
            status = cls._status_for_mastery(mastery)
            tenant_id = (student.tenant_id or "").strip()

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
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.outcome.code}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "student", "outcome"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_student_outcome_active",
            ),
        ]
        verbose_name = "Resultado do aluno"
        verbose_name_plural = "Resultados do aluno"
        ordering = ["-updated_at"]
