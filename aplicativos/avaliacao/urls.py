from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AvaliacaoViewSet, ComponenteAvaliativaViewSet, PeriodoAvaliativoViewSet, ResultadoPeriodoDisciplinaViewSet

router = DefaultRouter()
router.register(r'periodos', PeriodoAvaliativoViewSet)
router.register(r'componentes', ComponenteAvaliativaViewSet)
router.register(r'avaliacoes', AvaliacaoViewSet)
router.register(r'resultados-periodo', ResultadoPeriodoDisciplinaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
