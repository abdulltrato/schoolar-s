from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AreaCurricularViewSet, DisciplinaViewSet, CompetenciaViewSet,
    CurriculoBaseViewSet, CurriculoLocalViewSet
)

router = DefaultRouter()
router.register(r'areas', AreaCurricularViewSet)
router.register(r'disciplinas', DisciplinaViewSet)
router.register(r'competencias', CompetenciaViewSet)
router.register(r'curriculos-base', CurriculoBaseViewSet)
router.register(r'curriculos-local', CurriculoLocalViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
