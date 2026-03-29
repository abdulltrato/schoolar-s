from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import Group

from core.admin_utils import TenantAwareAdmin

from .models import (
    AcademicYear,
    Grade,
    School,
    Teacher,
    TeacherSpecialty,
    Cycle,
    Classroom,
    GradeSubject,
    TeachingAssignment,
    Enrollment,
    ManagementAssignment,
    UserProfile,
    AttendanceRecord,
    Announcement,
    Invoice,
    Payment,
    AuditEvent,
    AuditAlert,
)


class EducationTrackFilter(admin.SimpleListFilter):
    title = "Ensino"
    parameter_name = "education_track"

    def lookups(self, request, model_admin):
        return (
            ("primary", "Primário"),
            ("secondary", "Secundário"),
            ("technical_professional", "Técnico Prof."),
        )

    def queryset(self, request, queryset):
        value = (self.value() or "").lower()
        if value == "primary":
            return queryset.filter(classroom__grade__number__lte=6)
        if value == "secondary":
            return queryset.filter(classroom__grade__number__gte=7, classroom__grade__number__lte=12)
        if value == "technical_professional":
            return queryset.filter(classroom__grade__number__gte=13)
        return queryset


class CycleBandFilter(admin.SimpleListFilter):
    title = "Ciclo / Nível"
    parameter_name = "cycle_band"

    def lookups(self, request, model_admin):
        return (
            ("primary_cycle_1", "Primário 1º ciclo"),
            ("primary_cycle_2", "Primário 2º ciclo"),
            ("secondary_cycle_1", "Secundário 1º ciclo"),
            ("secondary_cycle_2", "Secundário 2º ciclo"),
            ("technical_basic", "Técnico Básico"),
            ("technical_medium", "Técnico Médio"),
            ("technical_superior", "Técnico Superior"),
        )

    def queryset(self, request, queryset):
        value = (self.value() or "").lower()
        if value == "primary_cycle_1":
            return queryset.filter(classroom__grade__number__lte=3)
        if value == "primary_cycle_2":
            return queryset.filter(classroom__grade__number__gte=4, classroom__grade__number__lte=6)
        if value == "secondary_cycle_1":
            return queryset.filter(classroom__grade__number__gte=7, classroom__grade__number__lte=9)
        if value == "secondary_cycle_2":
            return queryset.filter(classroom__grade__number__gte=10, classroom__grade__number__lte=12)
        if value == "technical_basic":
            return queryset.filter(classroom__grade__number__gte=13, classroom__grade__number__lte=15)
        if value == "technical_medium":
            return queryset.filter(classroom__grade__number__gte=16, classroom__grade__number__lte=18)
        if value == "technical_superior":
            return queryset.filter(classroom__grade__number__gte=19)
        return queryset


@admin.register(AcademicYear)
class AcademicYearAdmin(TenantAwareAdmin):
    pass


@admin.register(Cycle)
class CycleAdmin(TenantAwareAdmin):
    list_display = ("code", "name", "track", "order")
    list_filter = ("track",)
    search_fields = ("code", "name")


@admin.register(Grade)
class GradeAdmin(TenantAwareAdmin):
    list_display = ("number", "name", "cycle", "cycle_model", "tenant_id", "deleted_at")
    list_filter = ("cycle", "cycle_model__track")


@admin.register(School)
class SchoolAdmin(TenantAwareAdmin):
    pass


@admin.register(Teacher)
class TeacherAdmin(TenantAwareAdmin):
    pass


@admin.register(TeacherSpecialty)
class TeacherSpecialtyAdmin(TenantAwareAdmin):
    list_display = ("name", "teacher", "tenant_id", "deleted_at")


@admin.register(Classroom)
class ClassroomAdmin(TenantAwareAdmin):
    list_display = ("name", "grade", "academic_year", "education_track", "tenant_id", "deleted_at")
    list_filter = ("academic_year__code", EducationTrackFilter, "grade__number")

    @admin.display(description="Ensino")
    def education_track(self, obj):
        if obj.grade_id and obj.grade.number:
            return "Técnico" if obj.grade.number > 12 else "Geral"
        return "-"


@admin.register(GradeSubject)
class GradeSubjectAdmin(TenantAwareAdmin):
    pass


@admin.register(TeachingAssignment)
class TeachingAssignmentAdmin(TenantAwareAdmin):
    pass


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


@admin.register(ManagementAssignment)
class ManagementAssignmentAdmin(TenantAwareAdmin):
    pass


@admin.register(UserProfile)
class UserProfileAdmin(TenantAwareAdmin):
    pass


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(TenantAwareAdmin):
    pass


@admin.register(Announcement)
class AnnouncementAdmin(TenantAwareAdmin):
    pass


@admin.register(Invoice)
class InvoiceAdmin(TenantAwareAdmin):
    pass


@admin.register(Payment)
class PaymentAdmin(TenantAwareAdmin):
    pass


@admin.register(AuditEvent)
class AuditEventAdmin(TenantAwareAdmin):
    pass


@admin.register(AuditAlert)
class AuditAlertAdmin(TenantAwareAdmin):
    pass


admin.site.unregister(Group)
admin.site.unregister(get_user_model())


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    fk_name = "user"
    can_delete = False
    extra = 0
    readonly_fields = ("tenant_id",)
    fields = ("tenant_id", "role", "school", "province", "district", "active")

    def has_add_permission(self, request, obj=None):
        if obj is None:
            return False
        try:
            getattr(obj, "school_profile")
            return False
        except Exception:
            return True


@admin.register(get_user_model())
class TenantUserAdmin(DefaultUserAdmin):
    inlines = [UserProfileInline]
    list_display = DefaultUserAdmin.list_display + ("tenant_id",)
    list_select_related = ("school_profile",)

    def get_inline_instances(self, request, obj=None):
        # On user creation (including admin popups), the profile is auto-created by signals.
        # Avoid rendering/saving an inline profile form during add, which can lead to duplicate
        # UserProfile creation and uniqueness validation errors.
        if obj is None:
            return []
        return super().get_inline_instances(request, obj=obj)

    def tenant_id(self, obj):
        return getattr(getattr(obj, "school_profile", None), "tenant_id", "")
    tenant_id.short_description = "Tenant"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        profile, _ = UserProfile.objects.get_or_create(user=obj)
        if request.user and hasattr(request.user, "school_profile"):
            profile_tenant = (request.user.school_profile.tenant_id or "").strip()
            if profile_tenant and profile.tenant_id != profile_tenant:
                profile.tenant_id = profile_tenant
        if not profile.tenant_id:
            profile.tenant_id = (getattr(request.user, "school_profile", None) and request.user.school_profile.tenant_id) or profile.tenant_id
        profile.save()
