from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseNamedCodeModel
from .period import AssessmentPeriod


class AssessmentComponent(BaseNamedCodeModel):
    CODE_PREFIX = "CMP"
    TYPE_CHOICES = [
        ("acs", "ACS"),
        ("acp", "ACP"),
        ("individual_work", "Trabalho individual"),
        ("group_work", "Trabalho em grupo"),
        ("test", "Teste"),
        ("exam", "Exame"),
        ("diagnostic", "Diagnóstica"),
        ("formative", "Formativa"),
        ("summative", "Summativa"),
        ("other", "Outra"),
    ]
    LEGACY_TYPE_MAP = {
        "teste": "test",
        "exame": "exam",
        "diagnostica": "diagnostic",
        "formativa": "formative",
        "sumativa": "summative",
        "outra": "other",
    }

    def __init__(self, *args, **kwargs):
        legacy_type = kwargs.pop("tipo", None)
        if legacy_type is not None and "type" not in kwargs:
            kwargs["type"] = legacy_type
        normalized_type = kwargs.get("type")
        if normalized_type is not None:
            kwargs["type"] = self.LEGACY_TYPE_MAP.get(normalized_type, normalized_type)
        super().__init__(*args, **kwargs)

    period = models.ForeignKey(AssessmentPeriod, on_delete=models.CASCADE, verbose_name="Período")
    grade_subject = models.ForeignKey("school.GradeSubject", on_delete=models.CASCADE, verbose_name="Disciplina da classe")
    type = models.CharField(max_length=30, choices=TYPE_CHOICES, verbose_name="Tipo")
    weight = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Peso")
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=20, verbose_name="Nota máxima")
    mandatory = models.BooleanField(default=True, verbose_name="Obrigatória")

    def clean(self):
        self.type = self.LEGACY_TYPE_MAP.get(self.type, self.type)
        if self.period.academic_year_id != self.grade_subject.academic_year_id:
            raise ValidationError({"grade_subject": "The grade subject must belong to the same academic year as the period."})
        period_tenant = (self.period.tenant_id or "").strip() if self.period_id else ""
        grade_subject_tenant = (self.grade_subject.tenant_id or "").strip() if self.grade_subject_id else ""
        if period_tenant and grade_subject_tenant and period_tenant != grade_subject_tenant:
            raise ValidationError({"tenant_id": "Assessment component tenant must match across period and grade subject."})
        if self.tenant_id and period_tenant and self.tenant_id != period_tenant:
            raise ValidationError({"tenant_id": "Assessment component tenant must match the period tenant."})
        if self.tenant_id and grade_subject_tenant and self.tenant_id != grade_subject_tenant:
            raise ValidationError({"tenant_id": "Assessment component tenant must match the grade subject tenant."})
        self.tenant_id = self.tenant_id or period_tenant or grade_subject_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id is required."})
        if self.weight <= 0 or self.weight > 100:
            raise ValidationError({"weight": "Weight must be between 0 and 100."})
        if self.max_score <= 0:
            raise ValidationError({"max_score": "Maximum score must be positive."})

    def save(self, *args, **kwargs):
        self.type = self.LEGACY_TYPE_MAP.get(self.type, self.type)
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.grade_subject.subject}"

    class Meta:
        verbose_name = "Componente avaliativa"
        verbose_name_plural = "Componentes avaliativas"
        ordering = ["period__academic_year__code", "period__order", "grade_subject__subject__name", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["period", "grade_subject", "name"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_assessment_component_active",
            ),
        ]
