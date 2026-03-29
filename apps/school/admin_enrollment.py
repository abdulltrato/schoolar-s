from django.contrib import admin

from core.admin_utils import TenantAwareAdmin
from .admin_filters import EducationTrackFilter, CycleBandFilter
from .models import Enrollment


@admin.register(Enrollment)
class EnrollmentAdmin(TenantAwareAdmin):
    list_display = (
        "student",
        "education_track",
        "cycle_band",
        "enrollment_year",
        "course_name",
        "duration_days",
        "tenant_id",
        "deleted_at",
    )
    list_select_related = ("student", "classroom", "classroom__academic_year", "classroom__grade")
    search_fields = ("student__name", "classroom__name", "classroom__academic_year__code")
    ordering = ("-enrollment_date",)
    list_filter = (
        "tenant_id",
        "classroom__academic_year__code",
        EducationTrackFilter,
        CycleBandFilter,
    )

    @admin.display(description="Ano letivo")
    def enrollment_year(self, obj):
        if obj.classroom_id and obj.classroom.academic_year_id and obj.classroom.academic_year.code:
            return obj.classroom.academic_year.code
        return obj.enrollment_date.year if obj.enrollment_date else "-"

    @admin.display(description="Curso / Turma")
    def course_name(self, obj):
        if obj.classroom_id:
            if obj.classroom.name:
                return obj.classroom.name
            if obj.classroom.grade_id and obj.classroom.grade.name:
                return obj.classroom.grade.name
        return "-"

    @admin.display(description="Duração (dias)")
    def duration_days(self, obj):
        if obj.classroom_id and obj.classroom.academic_year_id:
            ay = obj.classroom.academic_year
            if ay.start_date and ay.end_date:
                return (ay.end_date - ay.start_date).days
        return "-"

    @admin.display(description="Ensino")
    def education_track(self, obj):
        track, _ = self._track_and_band(obj)
        return {
            "primary": "Primário",
            "secondary": "Secundário",
            "technical_professional": "Técnico Prof.",
        }.get(track, "-")

    @admin.display(description="Ciclo / Nível")
    def cycle_band(self, obj):
        _, band = self._track_and_band(obj)
        labels = {
            "primary_cycle_1": "Primário 1º ciclo",
            "primary_cycle_2": "Primário 2º ciclo",
            "secondary_cycle_1": "Secundário 1º ciclo",
            "secondary_cycle_2": "Secundário 2º ciclo",
            "technical_basic": "Técnico Básico",
            "technical_medium": "Técnico Médio",
            "technical_superior": "Técnico Superior",
        }
        return labels.get(band, "-")

    @staticmethod
    def _track_and_band(obj):
        if not (obj.classroom_id and obj.classroom.grade_id):
            return None, None
        number = obj.classroom.grade.number
        track = "technical_professional" if number and number > 12 else ("primary" if number <= 6 else "secondary")

        if track == "primary":
            band = "primary_cycle_1" if number <= 3 else "primary_cycle_2"
        elif track == "secondary":
            band = "secondary_cycle_1" if number <= 9 else "secondary_cycle_2"
        else:
            if number <= 15:
                band = "technical_basic"
            elif number <= 18:
                band = "technical_medium"
            else:
                band = "technical_superior"
        return track, band
