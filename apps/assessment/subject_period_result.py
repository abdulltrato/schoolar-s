from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseCodeModel
from .assessment import Assessment
from .period import AssessmentPeriod


class SubjectPeriodResult(BaseCodeModel):
    CODE_PREFIX = "SPR"

    student = models.ForeignKey("academic.Student", on_delete=models.CASCADE, verbose_name="Aluno")
    teaching_assignment = models.ForeignKey("school.TeachingAssignment", on_delete=models.CASCADE, verbose_name="Alocação docente")
    period = models.ForeignKey(AssessmentPeriod, on_delete=models.CASCADE, verbose_name="Período")
    final_average = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Média final")
    assessments_counted = models.PositiveSmallIntegerField(default=0, verbose_name="Avaliações consideradas")

    @classmethod
    def recalculate(cls, *, student, teaching_assignment, period):
        assessments = Assessment.objects.filter(
            student=student,
            teaching_assignment=teaching_assignment,
            period=period,
            component__isnull=False,
            score__isnull=False,
        ).select_related("component")

        total_weight = Decimal("0")
        weighted_total = Decimal("0")

        for assessment in assessments:
            weight = Decimal(assessment.component.weight)
            max_score = Decimal(assessment.component.max_score)
            score = Decimal(assessment.score)
            normalized_score = (score / max_score) * Decimal("20")
            weighted_total += normalized_score * weight
            total_weight += weight

        total_assessments = assessments.count()
        if total_weight <= 0 or total_assessments == 0:
            cls.objects.filter(
                student=student,
                teaching_assignment=teaching_assignment,
                period=period,
            ).delete()
            return None

        final_average = weighted_total / total_weight

        tenant_id = (getattr(student, "tenant_id", "") or getattr(teaching_assignment, "tenant_id", "") or getattr(period, "tenant_id", "") or "").strip()
        result, _ = cls.all_objects.update_or_create(
            student=student,
            teaching_assignment=teaching_assignment,
            period=period,
            defaults={
                "tenant_id": tenant_id,
                "final_average": final_average.quantize(Decimal("0.01")),
                "assessments_counted": total_assessments,
                "deleted_at": None,
            },
        )
        return result

    @classmethod
    def recalcular(cls, *, student, teaching_assignment, period):
        return cls.recalculate(
            student=student,
            teaching_assignment=teaching_assignment,
            period=period,
        )

    def clean(self):
        student_tenant = (self.student.tenant_id or "").strip() if self.student_id else ""
        assignment_tenant = (self.teaching_assignment.tenant_id or "").strip() if self.teaching_assignment_id else ""
        period_tenant = (self.period.tenant_id or "").strip() if self.period_id else ""
        for related_tenant in [student_tenant, assignment_tenant, period_tenant]:
            if self.tenant_id and related_tenant and self.tenant_id != related_tenant:
                raise ValidationError({"tenant_id": "Result tenant must match related records."})
        if student_tenant and assignment_tenant and student_tenant != assignment_tenant:
            raise ValidationError({"tenant_id": "Student and teaching assignment must belong to the same tenant."})
        if period_tenant and assignment_tenant and period_tenant != assignment_tenant:
            raise ValidationError({"tenant_id": "Period and teaching assignment must belong to the same tenant."})
        self.tenant_id = self.tenant_id or student_tenant or assignment_tenant or period_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id is required."})
        if self.period.academic_year_id != self.teaching_assignment.classroom.academic_year_id:
            raise ValidationError({"period": "The period must belong to the same academic year as the teaching assignment."})
        if self.student.cycle != self.teaching_assignment.classroom.cycle or self.student.grade != self.teaching_assignment.classroom.grade.number:
            raise ValidationError({"student": "The student must belong to the teaching assignment classroom."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Result {self.student} - {self.teaching_assignment.grade_subject.subject} - {self.period}"

    class Meta:
        verbose_name = "Resultado por período e disciplina"
        verbose_name_plural = "Resultados por período e disciplina"
        ordering = ["period__academic_year__code", "period__order", "student__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "teaching_assignment", "period"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_subject_period_result_active",
            ),
        ]
