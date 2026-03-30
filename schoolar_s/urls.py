"""URL configuration do projeto schoolar_s."""

from django.contrib import admin
from django.urls import path, include
from .views import healthcheck, readiness

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", healthcheck, name="healthcheck"),
    path("ready/", readiness, name="readiness"),
    path("api/", include("schoolar_s.api.urls")),
]
