from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseNamedCodeModel


class AssessmentPeriod(BaseNamedCodeModel):
    CODE_PREFIX = "APR"

    academic_year = models.ForeignKey("school.AcademicYear", on_delete=models.CASCADE, verbose_name="Ano letivo")
    order = models.PositiveSmallIntegerField(verbose_name="Ordem")
    start_date = models.DateField(verbose_name="Data de início")
    end_date = models.DateField(verbose_name="Data de fim")
    active = models.BooleanField(default=True, verbose_name="Ativo")

    def clean(self):
        academic_tenant = (self.academic_year.tenant_id or "").strip() if self.academic_year_id else ""
        if academic_tenant:
            if self.tenant_id and self.tenant_id != academic_tenant:
                raise ValidationError({"tenant_id": "Assessment period tenant must match the academic year tenant."})
            if not self.tenant_id:
                self.tenant_id = academic_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id is required."})
        if self.end_date <= self.start_date:
            raise ValidationError({"end_date": "End date must be later than the start date."})
        if self.academic_year_id:
            year = self.academic_year
            if self.start_date < year.start_date or self.end_date > year.end_date:
                raise ValidationError({"start_date": "Assessment period must fall within the academic year."})
            overlapping = AssessmentPeriod.objects.filter(academic_year=year).exclude(pk=self.pk).filter(
                start_date__lte=self.end_date,
                end_date__gte=self.start_date,
            )
            if overlapping.exists():
                raise ValidationError({"start_date": "Assessment period overlaps with an existing period."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.academic_year}"

    class Meta:
        verbose_name = "Período avaliativo"
        verbose_name_plural = "Períodos avaliativos"
        ordering = ["academic_year__code", "order"]
        constraints = [
            models.UniqueConstraint(
                fields=["academic_year", "order"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_assessment_period_order_active",
            ),
        ]
