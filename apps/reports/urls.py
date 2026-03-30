from django.urls import include, path
# Utilidades de roteamento.
from rest_framework.routers import DefaultRouter
# Router padrão do DRF.

from .views import ReportViewSet
# ViewSet de relatórios.

router = DefaultRouter()
router.register(r"reports", ReportViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
