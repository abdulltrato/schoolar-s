from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseCodeModel
from .component import AssessmentComponent
from .period import AssessmentPeriod


class Assessment(BaseCodeModel):
    CODE_PREFIX = "ASM"
    TYPE_CHOICES = AssessmentComponent.TYPE_CHOICES

    def __init__(self, *args, **kwargs):
        legacy_type = kwargs.pop("tipo", None)
        legacy_date = kwargs.pop("data", None)
        if legacy_type is not None and "type" not in kwargs:
            kwargs["type"] = legacy_type
        if legacy_date is not None and "date" not in kwargs:
            kwargs["date"] = legacy_date
        normalized_type = kwargs.get("type")
        if normalized_type is not None:
            kwargs["type"] = AssessmentComponent.LEGACY_TYPE_MAP.get(normalized_type, normalized_type)
        super().__init__(*args, **kwargs)

    student = models.ForeignKey("academic.Student", on_delete=models.CASCADE, verbose_name="Aluno")
    teaching_assignment = models.ForeignKey(
        "school.TeachingAssignment",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Alocação docente",
    )
    period = models.ForeignKey(
        AssessmentPeriod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Período",
    )
    component = models.ForeignKey(
        AssessmentComponent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Componente",
    )
    competency = models.ForeignKey(
        "curriculum.Competency",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Competência",
    )
    type = models.CharField(max_length=30, choices=TYPE_CHOICES, verbose_name="Tipo")
    date = models.DateField(verbose_name="Data")
    score = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, verbose_name="Nota")
    comment = models.TextField(blank=True, verbose_name="Comentário")
    knowledge = models.BooleanField(default=False, verbose_name="Conhecimentos")
    skills = models.BooleanField(default=False, verbose_name="Habilidades")
    attitudes = models.BooleanField(default=False, verbose_name="Atitudes")

    def clean(self):
        self.type = AssessmentComponent.LEGACY_TYPE_MAP.get(self.type, self.type)
        if not self.teaching_assignment_id:
            raise ValidationError({"teaching_assignment": "A teaching assignment is required."})

        classroom = self.teaching_assignment.classroom
        subject = self.teaching_assignment.grade_subject.subject
        student_tenant = (self.student.tenant_id or "").strip() if self.student_id else ""
        classroom_tenant = (classroom.tenant_id or "").strip()

        if self.tenant_id and student_tenant and self.tenant_id != student_tenant:
            raise ValidationError({"tenant_id": "Assessment tenant must match the student tenant."})
        if self.tenant_id and classroom_tenant and self.tenant_id != classroom_tenant:
            raise ValidationError({"tenant_id": "Assessment tenant must match the classroom tenant."})
        if student_tenant and classroom_tenant and student_tenant != classroom_tenant:
            raise ValidationError({"tenant_id": "Assessment student and classroom must belong to the same tenant."})
        self.tenant_id = self.tenant_id or student_tenant or classroom_tenant

        if self.date and self.teaching_assignment_id:
            conflicts = (
                Assessment.objects.filter(
                    tenant_id=self.tenant_id,
                    teaching_assignment_id=self.teaching_assignment_id,
                    date=self.date,
                    deleted_at__isnull=True,
                )
                .exclude(pk=self.pk)
                .exists()
            )
            if conflicts:
                raise ValidationError({"date": "Já existe uma avaliação marcada para esta turma/disciplina nesta data."})

        if self.student_id:
            if self.student.cycle != classroom.cycle:
                raise ValidationError({"student": "Student and classroom must belong to the same cycle."})
            if self.student.grade != classroom.grade.number:
                raise ValidationError({"student": "Student and classroom must belong to the same grade."})
            enrolled = self.student.enrollment_set.filter(classroom=classroom).exists()
            if not enrolled:
                raise ValidationError({"student": "The student must be enrolled in the assessed classroom."})

        if self.competency_id and self.competency.subject_id != subject.id:
            raise ValidationError({"competency": "The competency must belong to the assessed subject."})

        if self.period_id and self.period.academic_year_id != classroom.academic_year_id:
            raise ValidationError({"period": "The period must belong to the same academic year as the classroom."})

        if self.component_id:
            if self.component.grade_subject_id != self.teaching_assignment.grade_subject_id:
                raise ValidationError({"component": "The component must belong to the same grade subject as the assessment."})
            if self.period_id and self.component.period_id != self.period_id:
                raise ValidationError({"component": "The component must belong to the same period."})
            self.type = self.component.type
            if self.score is not None and self.score > self.component.max_score:
                raise ValidationError({"score": "The score cannot exceed the component maximum score."})

        if self.score is not None and not 0 <= self.score <= 20:
            raise ValidationError({"score": "The score must be between 0 and 20."})

    def _result_key(self):
        if not self.student_id or not self.teaching_assignment_id or not self.period_id:
            return None
        return {
            "student": self.student,
            "teaching_assignment": self.teaching_assignment,
            "period": self.period,
        }

    def _sync_results(self, keys):
        from .subject_period_result import SubjectPeriodResult

        for key in keys:
            if key:
                SubjectPeriodResult.recalculate(**key)

    def _sync_outcomes(self, component_ids):
        if not self.student_id:
            return
        component_ids = [component_id for component_id in component_ids if component_id]
        if not component_ids:
            return
        from apps.academic.models import StudentOutcome

        StudentOutcome.recalculate_for_components(student=self.student, component_ids=component_ids)

    def save(self, *args, **kwargs):
        self.type = AssessmentComponent.LEGACY_TYPE_MAP.get(self.type, self.type)
        previous_key = None
        previous_component_id = None
        if self.pk:
            previous = type(self).objects.filter(pk=self.pk).select_related(
                "student",
                "teaching_assignment",
                "period",
                "component",
            ).first()
            if previous:
                previous_key = previous._result_key()
                previous_component_id = previous.component_id

        self.full_clean()
        result = super().save(*args, **kwargs)
        self._sync_results([previous_key, self._result_key()])
        self._sync_outcomes([previous_component_id, self.component_id])
        return result

    def delete(self, *args, **kwargs):
        current_key = self._result_key()
        component_id = self.component_id
        result = super().delete(*args, **kwargs)
        self._sync_results([current_key])
        self._sync_outcomes([component_id])
        return result

    def __str__(self):
        return f"{self.type} assessment for {self.student} in {self.teaching_assignment.grade_subject.subject}"

    class Meta:
        verbose_name = "Avaliação"
        verbose_name_plural = "Avaliações"
        ordering = ["-date"]
