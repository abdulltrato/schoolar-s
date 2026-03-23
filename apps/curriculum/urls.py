from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BaseCurriculumViewSet,
    CompetencyViewSet,
    CurriculumAreaViewSet,
    LocalCurriculumViewSet,
    SubjectCurriculumPlanViewSet,
    SubjectViewSet,
)

router = DefaultRouter()
router.register(r"areas", CurriculumAreaViewSet)
router.register(r"subjects", SubjectViewSet)
router.register(r"competencies", CompetencyViewSet)
router.register(r"base-curricula", BaseCurriculumViewSet)
router.register(r"local-curricula", LocalCurriculumViewSet)
router.register(r"subject-plans", SubjectCurriculumPlanViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
