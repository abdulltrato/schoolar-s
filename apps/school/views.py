from .views_academic import AcademicYearViewSet, GradeViewSet, GradeSubjectViewSet
# Viewsets relacionados a anos letivos e classes.
from .views_school import SchoolViewSet, ClassroomViewSet, TeacherViewSet, TeachingAssignmentViewSet
# Viewsets de escola, turmas e docentes.
from .views_enrollment import EnrollmentViewSet, AttendanceRecordViewSet
# Viewsets de matrículas e presença.
from .views_management import ManagementAssignmentViewSet, AnnouncementViewSet
# Viewsets de gestão escolar e comunicados.
from .views_finance import InvoiceViewSet, PaymentViewSet
# Viewsets de finanças (faturas/pagamentos).
from .views_audit import AuditAlertViewSet, AuditEventViewSet
# Viewsets de auditoria.
from .views_user import UserProfileViewSet
# Viewset de perfis de utilizador.

# Exporta todos os viewsets para import único.
__all__ = [
    "AcademicYearViewSet",
    "GradeViewSet",
    "GradeSubjectViewSet",
    "SchoolViewSet",
    "ClassroomViewSet",
    "TeacherViewSet",
    "TeachingAssignmentViewSet",
    "EnrollmentViewSet",
    "AttendanceRecordViewSet",
    "ManagementAssignmentViewSet",
    "AnnouncementViewSet",
    "InvoiceViewSet",
    "PaymentViewSet",
    "AuditEventViewSet",
    "AuditAlertViewSet",
    "UserProfileViewSet",
]
