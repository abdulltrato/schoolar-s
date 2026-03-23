from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AcademicYearViewSet,
    AuditAlertViewSet,
    AuditEventViewSet,
    AnnouncementViewSet,
    AttendanceRecordViewSet,
    ClassroomViewSet,
    EnrollmentViewSet,
    GradeSubjectViewSet,
    GradeViewSet,
    InvoiceViewSet,
    ManagementAssignmentViewSet,
    PaymentViewSet,
    SchoolViewSet,
    TeacherViewSet,
    TeachingAssignmentViewSet,
    UserProfileViewSet,
)

router = DefaultRouter()
router.register(r"academic-years", AcademicYearViewSet)
router.register(r"audit-alerts", AuditAlertViewSet)
router.register(r"audit-events", AuditEventViewSet)
router.register(r"grades", GradeViewSet)
router.register(r"schools", SchoolViewSet)
router.register(r"teachers", TeacherViewSet)
router.register(r"classrooms", ClassroomViewSet)
router.register(r"grade-subjects", GradeSubjectViewSet)
router.register(r"teaching-assignments", TeachingAssignmentViewSet)
router.register(r"management-assignments", ManagementAssignmentViewSet)
router.register(r"enrollments", EnrollmentViewSet)
router.register(r"user-profiles", UserProfileViewSet)
router.register(r"attendance-records", AttendanceRecordViewSet)
router.register(r"announcements", AnnouncementViewSet)
router.register(r"invoices", InvoiceViewSet)
router.register(r"payments", PaymentViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
