from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AssessmentComponentViewSet,
    AssessmentPeriodViewSet,
    AssessmentViewSet,
    SubjectPeriodResultViewSet,
)

router = DefaultRouter()
router.register(r"periods", AssessmentPeriodViewSet)
router.register(r"components", AssessmentComponentViewSet)
router.register(r"assessments", AssessmentViewSet)
router.register(r"subject-period-results", SubjectPeriodResultViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
