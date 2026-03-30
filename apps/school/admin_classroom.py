from django.contrib import admin
# Ferramentas do Django admin.

from core.admin_utils import TenantAwareAdmin
# Mixin com scoping de tenant.
from .admin_filters import EducationTrackFilter
# Filtro customizado por trilha de ensino.
from .models import Classroom
# Modelo de turma/sala.


@admin.register(Classroom)
class ClassroomAdmin(TenantAwareAdmin):
    """Administra turmas exibindo grade, ano letivo e trilha."""

    list_display = ("name", "grade", "academic_year", "education_track", "tenant_id", "deleted_at")
    list_filter = ("academic_year__code", EducationTrackFilter, "grade__number")

    @admin.display(description="Ensino")
    def education_track(self, obj):
        """Deriva trilha de ensino com base no número da classe."""
        if obj.grade_id and obj.grade.number:
            return "Técnico" if obj.grade.number > 12 else "Geral"
        return "-"
