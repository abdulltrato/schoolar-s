from django.urls import include, path
# Utilitários de roteamento do Django.
from rest_framework.routers import DefaultRouter
# Router padrão do DRF.

from .views import CertificateViewSet
# ViewSet principal de certificados.

# Registra rotas REST para certificados.
router = DefaultRouter()
router.register(r"certificates", CertificateViewSet)

# Exposição das URLs do router.
urlpatterns = [
    path("", include(router.urls)),
]
