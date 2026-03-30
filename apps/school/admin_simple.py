from django.contrib import admin
# Ferramentas de registro do Django admin.

from core.admin_utils import TenantAwareAdmin
# Mixin que aplica filtros e validação de tenant.
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
# Modelos escolares básicos.


@admin.register(AcademicYear)
class AcademicYearAdmin(TenantAwareAdmin):
    """Admin para anos letivos; usa filtros padrão de tenant."""
    pass


@admin.register(Cycle)
class CycleAdmin(TenantAwareAdmin):
    """Administra ciclos de ensino (ex.: primário/segundário)."""
    list_display = ("code", "name", "track", "order")
    list_filter = ("track",)
    search_fields = ("code", "name")


@admin.register(Grade)
class GradeAdmin(TenantAwareAdmin):
    """Admin de classes/anos escolares, exibindo ciclo e tenant."""
    list_display = ("number", "name", "cycle", "cycle_model", "tenant_id", "deleted_at")
    list_filter = ("cycle", "cycle_model__track")


@admin.register(School)
class SchoolAdmin(TenantAwareAdmin):
    """Administra escolas/tenants."""
    pass


@admin.register(Teacher)
class TeacherAdmin(TenantAwareAdmin):
    """Admin de professores."""
    pass


@admin.register(TeacherSpecialty)
class TeacherSpecialtyAdmin(TenantAwareAdmin):
    """Administra especialidades vinculadas a professores."""
    list_display = ("name", "teacher", "tenant_id", "deleted_at")


@admin.register(GradeSubject)
class GradeSubjectAdmin(TenantAwareAdmin):
    """Admin de disciplinas ofertadas por classe/ano."""
    pass


@admin.register(TeachingAssignment)
class TeachingAssignmentAdmin(TenantAwareAdmin):
    """Administra alocações de docentes em disciplinas."""
    pass


@admin.register(ManagementAssignment)
class ManagementAssignmentAdmin(TenantAwareAdmin):
    """Administra cargos de gestão atribuídos a usuários."""
    pass


@admin.register(UserProfile)
class UserProfileAdmin(TenantAwareAdmin):
    """Administra perfis de usuário com dados escolares."""
    pass


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(TenantAwareAdmin):
    """Administra registros de presença/assiduidade."""
    pass


@admin.register(Announcement)
class AnnouncementAdmin(TenantAwareAdmin):
    """Admin de comunicados internos."""
    pass


@admin.register(Invoice)
class InvoiceAdmin(TenantAwareAdmin):
    """Administra faturas geradas."""
    pass


@admin.register(Payment)
class PaymentAdmin(TenantAwareAdmin):
    """Administra pagamentos efetuados."""
    pass


@admin.register(AuditEvent)
class AuditEventAdmin(TenantAwareAdmin):
    """Admin de eventos de auditoria (rastreamento)."""
    pass


@admin.register(AuditAlert)
class AuditAlertAdmin(TenantAwareAdmin):
    """Admin de alertas derivados de eventos de auditoria."""
    pass
