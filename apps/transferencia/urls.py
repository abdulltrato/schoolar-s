from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TransferViewSet

router = DefaultRouter()
router.register(r"transfers", TransferViewSet)
router.register(r"transferencias", TransferViewSet, basename="legacy-transfers")

urlpatterns = [
    path("", include(router.urls)),
]

