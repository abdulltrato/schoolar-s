from django.urls import include, path
# Utilidades de roteamento do Django.
from rest_framework.routers import DefaultRouter
# Router padrão do DRF.

from .views import (
    AssignmentViewSet,
    CourseOfferingViewSet,
    CourseModuleViewSet,
    CourseViewSet,
    LessonMaterialViewSet,
    LessonViewSet,
    SubmissionViewSet,
    SubmissionAttachmentViewSet,
)
# Viewsets da app learning.

# Cria router e registra todos os recursos REST.
router = DefaultRouter()
router.register(r"courses", CourseViewSet)
router.register(r"course-modules", CourseModuleViewSet)
router.register(r"offerings", CourseOfferingViewSet)
router.register(r"lessons", LessonViewSet)
router.register(r"lesson-materials", LessonMaterialViewSet)
router.register(r"assignments", AssignmentViewSet)
router.register(r"submissions", SubmissionViewSet)
router.register(r"submission-attachments", SubmissionAttachmentViewSet)

# Expõe as rotas na raiz da app.
urlpatterns = [
    path("", include(router.urls)),
]
