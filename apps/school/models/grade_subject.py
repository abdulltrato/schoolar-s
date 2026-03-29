from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseCodeModel

from .academic_year import AcademicYear
from .cycle_grade import Grade


class GradeSubject(BaseCodeModel):
    CODE_PREFIX = "GDS"

    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, verbose_name="Ano letivo")
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, verbose_name="Classe")
    subject = models.ForeignKey("curriculum.Subject", on_delete=models.CASCADE, verbose_name="Disciplina")
    weekly_workload = models.PositiveSmallIntegerField(default=0, verbose_name="Carga horária semanal")

    def clean(self):
        if self.subject_id and self.grade_id and self.subject.cycle != self.grade.cycle:
            raise ValidationError({"subject": "A disciplina deve pertencer ao mesmo ciclo da classe."})
        academic_tenant = (self.academic_year.tenant_id or "").strip() if self.academic_year_id else ""
        if academic_tenant:
            if self.tenant_id and self.tenant_id != academic_tenant:
                raise ValidationError({"tenant_id": "O tenant da disciplina da classe deve coincidir com o tenant do ano letivo."})
            if not self.tenant_id:
                self.tenant_id = academic_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id é obrigatório."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.subject} - {self.grade} ({self.academic_year})"

    class Meta:
        verbose_name = "Disciplina da classe"
        verbose_name_plural = "Disciplinas da classe"
        ordering = ["academic_year__code", "grade__number", "subject__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "academic_year", "grade", "subject"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_grade_subject_active",
            ),
        ]
