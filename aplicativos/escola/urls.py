from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AlocacaoDocenteViewSet,
    AnoLetivoViewSet,
    AtribuicaoGestaoViewSet,
    ClasseViewSet,
    DisciplinaClasseViewSet,
    EscolaViewSet,
    MatriculaViewSet,
    ProfessorViewSet,
    TurmaViewSet,
)

router = DefaultRouter()
router.register(r'anos-letivos', AnoLetivoViewSet)
router.register(r'classes', ClasseViewSet)
router.register(r'escolas', EscolaViewSet)
router.register(r'professores', ProfessorViewSet)
router.register(r'turmas', TurmaViewSet)
router.register(r'disciplinas-classe', DisciplinaClasseViewSet)
router.register(r'alocacoes-docentes', AlocacaoDocenteViewSet)
router.register(r'atribuicoes-gestao', AtribuicaoGestaoViewSet)
router.register(r'matriculas', MatriculaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
