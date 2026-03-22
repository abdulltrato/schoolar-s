from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProgressaoViewSet

router = DefaultRouter()
router.register(r'progressoes', ProgressaoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
