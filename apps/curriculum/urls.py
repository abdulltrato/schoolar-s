from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BaseCurriculumViewSet,
    CompetencyOutcomeViewSet,
    CompetencyViewSet,
    CurriculumAreaViewSet,
    LearningOutcomeViewSet,
    LocalCurriculumViewSet,
    SubjectCurriculumPlanViewSet,
    SubjectViewSet,
)

router = DefaultRouter()
router.register(r"areas", CurriculumAreaViewSet)
router.register(r"subjects", SubjectViewSet)
router.register(r"disciplinas", SubjectViewSet, basename="legacy-subjects")
router.register(r"competencies", CompetencyViewSet)
router.register(r"base-curricula", BaseCurriculumViewSet)
router.register(r"curriculos-base", BaseCurriculumViewSet, basename="legacy-base-curricula")
router.register(r"local-curricula", LocalCurriculumViewSet)
router.register(r"curriculos-local", LocalCurriculumViewSet, basename="legacy-local-curricula")
router.register(r"subject-plans", SubjectCurriculumPlanViewSet)
router.register(r"learning-outcomes", LearningOutcomeViewSet)
router.register(r"competency-outcomes", CompetencyOutcomeViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
