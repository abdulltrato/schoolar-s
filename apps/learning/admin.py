from django.contrib import admin

from core.admin_utils import TenantAwareAdmin

from .models import (
    Course,
    CourseModule,
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


class CourseModuleInline(admin.TabularInline):
    model = CourseModule
    extra = 1
    fields = ("subject", "name", "workload_hours", "required", "order")
    autocomplete_fields = ("subject",)
    can_delete = True


@admin.register(Course)
class CourseAdmin(TenantAwareAdmin):
    inlines = [CourseModuleInline, CourseStudentInline]
    filter_horizontal = ("curriculum_areas",)


@admin.register(CourseOffering)
class CourseOfferingAdmin(TenantAwareAdmin):
    pass


@admin.register(Lesson)
class LessonAdmin(TenantAwareAdmin):
    pass


@admin.register(LessonMaterial)
class LessonMaterialAdmin(TenantAwareAdmin):
    list_display = ("title", "lesson_title", "course_title", "classroom_name", "material_type", "required")
    readonly_fields = ("lesson", "lesson_title", "course_title", "classroom_name")

    def lesson_title(self, obj):
        return obj.lesson.title if obj.lesson_id else None

    def course_title(self, obj):
        return obj.lesson.offering.course.title if obj.lesson_id and obj.lesson.offering_id else None

    def classroom_name(self, obj):
        return obj.lesson.offering.classroom.name if obj.lesson_id and obj.lesson.offering_id and obj.lesson.offering.classroom_id else None

    lesson_title.short_description = "Aula"
    course_title.short_description = "Curso"
    classroom_name.short_description = "Turma"


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
