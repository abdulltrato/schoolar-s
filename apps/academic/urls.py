from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import GuardianViewSet, StudentGuardianViewSet, StudentOutcomeViewSet, StudentViewSet

router = DefaultRouter()
router.register(r"students", StudentViewSet)
router.register(r"alunos", StudentViewSet, basename="legacy-students")
router.register(r"guardians", GuardianViewSet)
router.register(r"student-guardians", StudentGuardianViewSet)
router.register(r"student-outcomes", StudentOutcomeViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
