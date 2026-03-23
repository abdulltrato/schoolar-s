from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models


class AssessmentPeriod(models.Model):
    academic_year = models.ForeignKey("school.AcademicYear", on_delete=models.CASCADE, verbose_name="Ano letivo")
    tenant_id = models.CharField(max_length=50, blank=True, verbose_name="Identificador do tenant")
    name = models.CharField(max_length=50, verbose_name="Nome")
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
        unique_together = ("academic_year", "order")


class AssessmentComponent(models.Model):
    TYPE_CHOICES = [
        ("acs", "ACS"),
        ("acp", "ACP"),
        ("individual_work", "Trabalho individual"),
        ("group_work", "Trabalho em grupo"),
        ("test", "Teste"),
        ("exam", "Exame"),
        ("diagnostic", "Diagnóstica"),
        ("formative", "Formativa"),
        ("summative", "Sumativa"),
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
    tenant_id = models.CharField(max_length=50, blank=True, verbose_name="Identificador do tenant")
    type = models.CharField(max_length=30, choices=TYPE_CHOICES, verbose_name="Tipo")
    name = models.CharField(max_length=80, verbose_name="Nome")
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
        unique_together = ("period", "grade_subject", "name")


class AssessmentOutcomeMap(models.Model):
    component = models.ForeignKey(AssessmentComponent, on_delete=models.CASCADE, verbose_name="Componente")
    outcome = models.ForeignKey("curriculum.LearningOutcome", on_delete=models.CASCADE, verbose_name="Resultado de aprendizagem")
    tenant_id = models.CharField(max_length=50, blank=True, verbose_name="Identificador do tenant")
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
        unique_together = ("tenant_id", "component", "outcome")


class Assessment(models.Model):
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
    tenant_id = models.CharField(max_length=50, blank=True, verbose_name="Identificador do tenant")
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


class SubjectPeriodResult(models.Model):
    student = models.ForeignKey("academic.Student", on_delete=models.CASCADE, verbose_name="Aluno")
    teaching_assignment = models.ForeignKey("school.TeachingAssignment", on_delete=models.CASCADE, verbose_name="Alocação docente")
    period = models.ForeignKey(AssessmentPeriod, on_delete=models.CASCADE, verbose_name="Período")
    tenant_id = models.CharField(max_length=50, blank=True, verbose_name="Identificador do tenant")
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
        result, _ = cls.objects.update_or_create(
            student=student,
            teaching_assignment=teaching_assignment,
            period=period,
            defaults={
                "tenant_id": tenant_id,
                "final_average": final_average.quantize(Decimal("0.01")),
                "assessments_counted": total_assessments,
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
        unique_together = ("student", "teaching_assignment", "period")
