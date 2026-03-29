from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseCodeModel
from core.tenant_mixins import TenantValidationMixin
from .validators import validate_offering_conflicts


class Course(BaseCodeModel, TenantValidationMixin):
    CODE_PREFIX = "CRS"
    MODALITY_CHOICES = [
        ("online", "Online"),
        ("blended", "Híbrido"),
        ("offline", "Presencial"),
    ]

    school = models.ForeignKey("school.School", on_delete=models.CASCADE, verbose_name="Escola")
    cycle_model = models.ForeignKey(
        "school.Cycle",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="courses",
        verbose_name="Ciclo",
    )
    title = models.CharField(max_length=180, verbose_name="Título")
    description = models.TextField(blank=True, verbose_name="Descrição")
    modality = models.CharField(max_length=20, choices=MODALITY_CHOICES, default="online", verbose_name="Modalidade")
    active = models.BooleanField(default=True, verbose_name="Ativo")

    def clean(self):
        school_tenant = ""
        if self.school_id and hasattr(self.school, "tenant_id"):
            school_tenant = (self.school.tenant_id or "").strip()
        if self.tenant_id and school_tenant and self.tenant_id != school_tenant:
            raise ValidationError({"tenant_id": "O tenant do curso deve coincidir com o tenant da escola."})
        self.ensure_tenant(school_tenant, self.tenant_id)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"
        ordering = ["title"]


class CourseOffering(BaseCodeModel, TenantValidationMixin):
    CODE_PREFIX = "COF"
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="offerings", verbose_name="Curso")
    classroom = models.ForeignKey("school.Classroom", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Turma")
    teacher = models.ForeignKey("school.Teacher", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Professor")
    academic_year = models.ForeignKey("school.AcademicYear", on_delete=models.CASCADE, verbose_name="Ano letivo")
    start_date = models.DateField(verbose_name="Data de início")
    end_date = models.DateField(verbose_name="Data de fim")
    active = models.BooleanField(default=True, verbose_name="Ativa")

    def clean(self):
        course_tenant = (self.course.tenant_id or "").strip() if self.course_id else ""
        classroom_tenant = (self.classroom.tenant_id or "").strip() if self.classroom_id else ""
        teacher_tenant = (self.teacher.tenant_id or "").strip() if self.teacher_id else ""
        academic_year_tenant = (self.academic_year.tenant_id or "").strip() if self.academic_year_id else ""
        for related_tenant in [classroom_tenant, teacher_tenant]:
            if course_tenant and related_tenant and course_tenant != related_tenant:
                raise ValidationError({"tenant_id": "As relações da oferta do curso devem pertencer ao mesmo tenant."})
        if academic_year_tenant and course_tenant and academic_year_tenant != course_tenant:
            raise ValidationError({"academic_year": "O ano letivo deve pertencer ao mesmo tenant do curso."})
        if self.tenant_id and course_tenant and self.tenant_id != course_tenant:
            raise ValidationError({"tenant_id": "O tenant da oferta do curso deve coincidir com o tenant do curso."})
        self.ensure_tenant(course_tenant, classroom_tenant, teacher_tenant, academic_year_tenant, self.tenant_id)
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValidationError({"end_date": "A data de fim deve ser posterior à data de início."})
        if self.classroom_id and self.course_id:
            course_school_id = self.course.school_id
            classroom_school_id = self.classroom.school_id
            if course_school_id and classroom_school_id and course_school_id != classroom_school_id:
                raise ValidationError({"classroom": "A turma deve pertencer à mesma escola do curso."})
        if self.teacher_id and self.course_id:
            course_school_id = self.course.school_id
            teacher_school_id = self.teacher.school_id
            if course_school_id and teacher_school_id and course_school_id != teacher_school_id:
                raise ValidationError({"teacher": "O professor deve pertencer à mesma escola do curso."})
        if self.teacher_id and self.classroom_id:
            teacher_school_id = self.teacher.school_id
            classroom_school_id = self.classroom.school_id
            if teacher_school_id and classroom_school_id and teacher_school_id != classroom_school_id:
                raise ValidationError({"teacher": "O professor deve pertencer à mesma escola da turma."})
        validate_offering_conflicts(self)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.course} - {self.academic_year}"

    class Meta:
        verbose_name = "Oferta do curso"
        verbose_name_plural = "Ofertas do curso"
        ordering = ["-academic_year__code", "course__title"]
