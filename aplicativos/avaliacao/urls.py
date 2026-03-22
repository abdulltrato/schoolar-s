from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AvaliacaoViewSet

router = DefaultRouter()
router.register(r'avaliacoes', AvaliacaoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
