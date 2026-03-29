from django.contrib import admin

from core.admin_utils import TenantAwareAdmin
from .models import (
    AcademicYear,
    Grade,
    School,
    Teacher,
    TeacherSpecialty,
    Cycle,
    GradeSubject,
    TeachingAssignment,
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


@admin.register(GradeSubject)
class GradeSubjectAdmin(TenantAwareAdmin):
    pass


@admin.register(TeachingAssignment)
class TeachingAssignmentAdmin(TenantAwareAdmin):
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
