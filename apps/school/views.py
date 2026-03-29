from .views_academic import AcademicYearViewSet, GradeViewSet, GradeSubjectViewSet
from .views_school import SchoolViewSet, ClassroomViewSet, TeacherViewSet, TeachingAssignmentViewSet
from .views_enrollment import EnrollmentViewSet, AttendanceRecordViewSet
from .views_management import ManagementAssignmentViewSet, AnnouncementViewSet
from .views_finance import InvoiceViewSet, PaymentViewSet
from .views_audit import AuditAlertViewSet, AuditEventViewSet
from .views_user import UserProfileViewSet

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
