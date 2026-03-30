from django.urls import include, path
# Utilidades de roteamento do Django.
from rest_framework.routers import DefaultRouter
# Router padrão do DRF.

from .views import TransferViewSet
# ViewSet de transferências.

# Cria router e registra rotas, incluindo alias legado.
router = DefaultRouter()
router.register(r"transfers", TransferViewSet)
router.register(r"transferencias", TransferViewSet, basename="legacy-transfers")

# Expõe rotas na raiz da app.
urlpatterns = [
    path("", include(router.urls)),
]
