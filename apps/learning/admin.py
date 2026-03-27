from django.contrib import admin

from core.admin_utils import TenantAwareAdmin

from .models import (
    Course,
    CourseOffering,
    Lesson,
    LessonMaterial,
    Assignment,
    Submission,
)


@admin.register(Course)
class CourseAdmin(TenantAwareAdmin):
    pass


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
    pass
