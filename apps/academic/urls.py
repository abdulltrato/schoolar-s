from django.urls import include, path
from rest_framework.routers import DefaultRouter

# Importa os viewsets que serão expostos via roteador REST.
from .views import GuardianViewSet, StudentGuardianViewSet, StudentOutcomeViewSet, StudentViewSet

# Cria o roteador padrão do DRF.
router = DefaultRouter()
# Registra endpoint CRUD para alunos (rota principal em inglês).
router.register(r"students", StudentViewSet)
# Registra rota alternativa legado em português mantendo mesma lógica.
router.register(r"alunos", StudentViewSet, basename="legacy-students")
# Registra endpoints para encarregados.
router.register(r"guardians", GuardianViewSet)
# Registra endpoints para vínculos aluno-encarregado.
router.register(r"student-guardians", StudentGuardianViewSet)
# Registra endpoints para resultados de aprendizagem.
router.register(r"student-outcomes", StudentOutcomeViewSet)

# Expõe todas as rotas geradas pelo roteador embaixo do path raiz.
urlpatterns = [
    path("", include(router.urls)),
]
