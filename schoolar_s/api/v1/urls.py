from django.urls import include, path

from schoolar_s.views import login_view, logout_view, me_view

urlpatterns = [
    path("auth/login/", login_view, name="auth-login"),
    path("auth/logout/", logout_view, name="auth-logout"),
    path("auth/me/", me_view, name="auth-me"),
    path("academic/", include("apps.academic.urls")),
    path("curriculum/", include("apps.curriculum.urls")),
    path("assessment/", include("apps.assessment.urls")),
    path("learning/", include("apps.learning.urls")),
    path("progress/", include("apps.progress.urls")),
    path("school/", include("apps.school.urls")),
    path("reports/", include("apps.reports.urls")),
    path("events/", include("apps.events.urls")),
    path("transfer/", include("apps.transfer.urls")),
    path("transferencia/", include("apps.transfer.urls")),
]
