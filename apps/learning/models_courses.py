from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseCodeModel
from core.tenant_mixins import TenantValidationMixin
from .validators import validate_offering_conflicts
from apps.curriculum.models import CurriculumArea, Subject


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
    curriculum_areas = models.ManyToManyField(
        CurriculumArea,
        related_name="courses",
        verbose_name="Áreas curriculares",
    )

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


class CourseModule(BaseCodeModel, TenantValidationMixin):
    CODE_PREFIX = "CMO"
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules", verbose_name="Curso")
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name="course_modules", verbose_name="Disciplina")
    name = models.CharField(max_length=180, blank=True, verbose_name="Nome do módulo")
    workload_hours = models.PositiveSmallIntegerField(default=0, verbose_name="Carga horária (h)")
    required = models.BooleanField(default=True, verbose_name="Obrigatório para certificar")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="Ordem")

    def clean(self):
        course_tenant = (self.course.tenant_id or "").strip() if self.course_id else ""
        subject_tenant = (self.subject.tenant_id or "").strip() if hasattr(self.subject, "tenant_id") else ""
        if self.tenant_id and course_tenant and self.tenant_id != course_tenant:
            raise ValidationError({"tenant_id": "O módulo deve pertencer ao mesmo tenant do curso."})
        if course_tenant and subject_tenant and course_tenant != subject_tenant:
            # We allow subject without tenant; otherwise must match.
            raise ValidationError({"subject": "A disciplina deve pertencer ao mesmo tenant do curso."})
        if not self.tenant_id:
            self.tenant_id = course_tenant or subject_tenant
        if not self.name:
            self.name = self.subject.name if self.subject_id else ""

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.course} - {self.name or self.subject}"

    class Meta:
        verbose_name = "Módulo do curso"
        verbose_name_plural = "Módulos do curso"
        ordering = ["course__title", "order", "subject__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["course", "subject"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_course_subject_module_active",
            )
        ]


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
