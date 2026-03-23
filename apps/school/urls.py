from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AcademicYearViewSet,
    ClassroomViewSet,
    EnrollmentViewSet,
    GradeSubjectViewSet,
    GradeViewSet,
    ManagementAssignmentViewSet,
    SchoolViewSet,
    TeacherViewSet,
    TeachingAssignmentViewSet,
)

router = DefaultRouter()
router.register(r"academic-years", AcademicYearViewSet)
router.register(r"grades", GradeViewSet)
router.register(r"schools", SchoolViewSet)
router.register(r"teachers", TeacherViewSet)
router.register(r"classrooms", ClassroomViewSet)
router.register(r"grade-subjects", GradeSubjectViewSet)
router.register(r"teaching-assignments", TeachingAssignmentViewSet)
router.register(r"management-assignments", ManagementAssignmentViewSet)
router.register(r"enrollments", EnrollmentViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
