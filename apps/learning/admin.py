from django.contrib import admin

from core.admin_utils import TenantAwareAdmin

from .models import (
    Course,
    CourseOffering,
    Lesson,
    LessonMaterial,
    Assignment,
    Submission,
    SubmissionAttachment,
)
from apps.academic.models import Student


class SubmissionAttachmentInline(admin.TabularInline):
    model = SubmissionAttachment
    extra = 1
    fields = ("enabled", "title", "description", "file")
    can_delete = True


class CourseStudentInline(admin.TabularInline):
    model = Student.courses.through
    extra = 1
    verbose_name = "Aluno inscrito"
    verbose_name_plural = "Alunos inscritos"
    autocomplete_fields = ["student"]
    fields = ("student",)
    can_delete = True


@admin.register(Course)
class CourseAdmin(TenantAwareAdmin):
    inlines = [CourseStudentInline]


@admin.register(CourseOffering)
class CourseOfferingAdmin(TenantAwareAdmin):
    pass


@admin.register(Lesson)
class LessonAdmin(TenantAwareAdmin):
    pass


@admin.register(LessonMaterial)
class LessonMaterialAdmin(TenantAwareAdmin):
    pass


@admin.register(Assignment)
class AssignmentAdmin(TenantAwareAdmin):
    pass


@admin.register(Submission)
class SubmissionAdmin(TenantAwareAdmin):
    inlines = [SubmissionAttachmentInline]
    readonly_fields = ("created_at", "updated_at", "deleted_at", "usuario")
    fieldsets = (
        (
            "Submissão da aula",
            {
                "fields": (
                    "tenant_id",
                    "assignment",
                    "student",
                    "submitted_at",
                    "status",
                    "text_response",
                    "attachment_url",
                    "score",
                    "feedback",
                )
            },
        ),
        (
            "Arquivos da aula",
            {
                "fields": (),
                "description": "Use a seção de anexos inline abaixo para carregar links e arquivos da submissão.",
            },
        ),
        (
            "Auditoria",
            {
                "fields": ("usuario", "created_at", "updated_at", "deleted_at"),
                "classes": ("collapse",),
            },
        ),
    )
