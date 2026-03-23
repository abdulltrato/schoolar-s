from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AssignmentViewSet,
    CourseOfferingViewSet,
    CourseViewSet,
    LessonMaterialViewSet,
    LessonViewSet,
    SubmissionViewSet,
)

router = DefaultRouter()
router.register(r"courses", CourseViewSet)
router.register(r"offerings", CourseOfferingViewSet)
router.register(r"lessons", LessonViewSet)
router.register(r"lesson-materials", LessonMaterialViewSet)
router.register(r"assignments", AssignmentViewSet)
router.register(r"submissions", SubmissionViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
