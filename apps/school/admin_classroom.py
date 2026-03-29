from django.contrib import admin

from core.admin_utils import TenantAwareAdmin
from .admin_filters import EducationTrackFilter
from .models import Classroom


@admin.register(Classroom)
class ClassroomAdmin(TenantAwareAdmin):
    list_display = ("name", "grade", "academic_year", "education_track", "tenant_id", "deleted_at")
    list_filter = ("academic_year__code", EducationTrackFilter, "grade__number")

    @admin.display(description="Ensino")
    def education_track(self, obj):
        if obj.grade_id and obj.grade.number:
            return "Técnico" if obj.grade.number > 12 else "Geral"
        return "-"
