from django.urls import include, path
# Funções utilitárias para composição de URLs.
from rest_framework.routers import DefaultRouter
# Router padrão do DRF para ViewSets.

from .views import (
    AssessmentComponentViewSet,
    AssessmentOutcomeMapViewSet,
    AssessmentPeriodViewSet,
    AssessmentViewSet,
    SubjectPeriodResultViewSet,
)
# Importa os viewsets expostos pela aplicação.

# Instancia router e registra endpoints REST.
router = DefaultRouter()
router.register(r"periods", AssessmentPeriodViewSet)
router.register(r"components", AssessmentComponentViewSet)
router.register(r"component-outcomes", AssessmentOutcomeMapViewSet)
router.register(r"assessments", AssessmentViewSet)
router.register(r"subject-period-results", SubjectPeriodResultViewSet)

# Define URLs públicas do app.
urlpatterns = [
    path("", include(router.urls)),
]
