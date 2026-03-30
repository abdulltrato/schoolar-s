from django.urls import include, path
# Utilidades de roteamento do Django.
from rest_framework.routers import DefaultRouter
# Router padrão do DRF para ViewSets.

from .views import (
    BaseCurriculumViewSet,
    CompetencyOutcomeViewSet,
    CompetencyViewSet,
    CurriculumAreaViewSet,
    LearningOutcomeViewSet,
    LocalCurriculumViewSet,
    SubjectSpecialtyViewSet,
    SubjectCurriculumPlanViewSet,
    SubjectViewSet,
)
# ViewSets registrados nas rotas da app.

# Cria router com rotas REST automáticas.
router = DefaultRouter()
# Área curricular.
router.register(r"areas", CurriculumAreaViewSet)
# Disciplinas.
router.register(r"subjects", SubjectViewSet)
# Alias legado para disciplinas.
router.register(r"disciplinas", SubjectViewSet, basename="legacy-subjects")
# Especialidades de disciplina.
router.register(r"subject-specialties", SubjectSpecialtyViewSet)
# Alias legado para especialidades.
router.register(r"especialidades", SubjectSpecialtyViewSet, basename="legacy-subject-specialties")
# Competências.
router.register(r"competencies", CompetencyViewSet)
# Currículos base.
router.register(r"base-curricula", BaseCurriculumViewSet)
# Alias legado para currículos base.
router.register(r"curriculos-base", BaseCurriculumViewSet, basename="legacy-base-curricula")
# Currículos locais.
router.register(r"local-curricula", LocalCurriculumViewSet)
# Alias legado para currículos locais.
router.register(r"curriculos-local", LocalCurriculumViewSet, basename="legacy-local-curricula")
# Planos curriculares por disciplina.
router.register(r"subject-plans", SubjectCurriculumPlanViewSet)
# Resultados de aprendizagem.
router.register(r"learning-outcomes", LearningOutcomeViewSet)
# Alinhamentos entre competências e resultados.
router.register(r"competency-outcomes", CompetencyOutcomeViewSet)

# Inclui rotas do router na raiz da app.
urlpatterns = [
    path("", include(router.urls)),
]
