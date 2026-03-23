"""
URL configuration for schoolar_s project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from .views import healthcheck, login_view, logout_view, me_view, readiness

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", healthcheck, name="healthcheck"),
    path("ready/", readiness, name="readiness"),
    path("api/v1/auth/login/", login_view, name="auth-login"),
    path("api/v1/auth/logout/", logout_view, name="auth-logout"),
    path("api/v1/auth/me/", me_view, name="auth-me"),
    path("api/v1/", include([
        path("academic/", include("apps.academic.urls")),
        path("curriculum/", include("apps.curriculum.urls")),
        path("assessment/", include("apps.assessment.urls")),
        path("learning/", include("apps.learning.urls")),
        path("progress/", include("apps.progress.urls")),
        path("school/", include("apps.school.urls")),
        path("reports/", include("apps.reports.urls")),
        path("events/", include("apps.events.urls")),
    ])),
]
