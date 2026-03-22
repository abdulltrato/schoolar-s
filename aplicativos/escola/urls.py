from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProfessorViewSet, TurmaViewSet, MatriculaViewSet

router = DefaultRouter()
router.register(r'professores', ProfessorViewSet)
router.register(r'turmas', TurmaViewSet)
router.register(r'matriculas', MatriculaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
