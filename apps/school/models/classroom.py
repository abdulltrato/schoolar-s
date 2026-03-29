from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseNamedCodeModel

from .cycle_grade import Cycle, Grade
from .academic_year import AcademicYear
from .school import School
from .teacher import Teacher


class Classroom(BaseNamedCodeModel):
    CODE_PREFIX = "CLS"

    school = models.ForeignKey(
        School,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="classrooms",
        verbose_name="Escola",
    )
    grade = models.ForeignKey(Grade, on_delete=models.PROTECT, null=True, blank=True, verbose_name="Classe")
    cycle = models.IntegerField(verbose_name="Ciclo")
    cycle_model = models.ForeignKey(
        Cycle,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="classrooms",
        verbose_name="Ciclo (model)",
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Ano letivo",
    )
    lead_teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Diretor de turma",
    )

    def clean(self):
        if not self.grade_id:
            raise ValidationError({"grade": "A turma deve estar associada a uma classe."})
        if not self.academic_year_id:
            raise ValidationError({"academic_year": "A turma deve estar associada a um ano letivo."})

        school_tenant = (self.school.tenant_id or "").strip() if self.school_id else ""
        academic_tenant = (self.academic_year.tenant_id or "").strip() if self.academic_year_id else ""
        if school_tenant:
            if self.tenant_id and self.tenant_id != school_tenant:
                raise ValidationError({"tenant_id": "O tenant da turma deve coincidir com o tenant da escola."})
            if not self.tenant_id:
                self.tenant_id = school_tenant
        if academic_tenant:
            if self.tenant_id and self.tenant_id != academic_tenant:
                raise ValidationError({"tenant_id": "O tenant da turma deve coincidir com o tenant do ano letivo."})
            if school_tenant and academic_tenant != school_tenant:
                raise ValidationError({"academic_year": "O ano letivo deve pertencer ao mesmo tenant da escola."})
            if not self.tenant_id:
                self.tenant_id = academic_tenant

        if self.lead_teacher_id and self.school_id and self.lead_teacher.school_id:
            if self.lead_teacher.school_id != self.school_id:
                raise ValidationError({"lead_teacher": "O diretor de turma deve pertencer à mesma escola."})
            if self.lead_teacher.tenant_id:
                if self.tenant_id and self.tenant_id != self.lead_teacher.tenant_id:
                    raise ValidationError({"tenant_id": "O tenant da turma deve coincidir com o tenant do diretor de turma."})
                if not self.tenant_id:
                    self.tenant_id = self.lead_teacher.tenant_id

        if self.grade_id:
            self.cycle = self.grade.cycle
            if not self.cycle_model_id and self.grade.cycle_model_id:
                self.cycle_model = self.grade.cycle_model
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id é obrigatório."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.academic_year}"

    class Meta:
        verbose_name = "Turma"
        verbose_name_plural = "Turmas"
        ordering = ["academic_year__code", "grade__number", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "name", "grade", "academic_year"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_classroom_active",
            ),
        ]
