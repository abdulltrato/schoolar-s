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


@admin.register(AcademicYear)
class AcademicYearAdmin(TenantAwareAdmin):
    pass


@admin.register(Grade)
class GradeAdmin(TenantAwareAdmin):
    pass


@admin.register(School)
class SchoolAdmin(TenantAwareAdmin):
    pass


@admin.register(Teacher)
class TeacherAdmin(TenantAwareAdmin):
    pass


@admin.register(Classroom)
class ClassroomAdmin(TenantAwareAdmin):
    pass


@admin.register(GradeSubject)
class GradeSubjectAdmin(TenantAwareAdmin):
    pass


@admin.register(TeachingAssignment)
class TeachingAssignmentAdmin(TenantAwareAdmin):
    pass


@admin.register(Enrollment)
class EnrollmentAdmin(TenantAwareAdmin):
    pass


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


@admin.register(get_user_model())
class TenantUserAdmin(DefaultUserAdmin):
    inlines = [UserProfileInline]
    list_display = DefaultUserAdmin.list_display + ("tenant_id",)
    list_select_related = ("school_profile",)

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
