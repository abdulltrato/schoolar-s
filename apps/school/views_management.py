from core.viewsets import RobustModelViewSet
# ViewSet base com tratamento robusto de exceções.
from .models import Announcement, ManagementAssignment
# Modelos de comunicados e cargos de gestão.
from .serializers import AnnouncementSerializer, ManagementAssignmentSerializer
# Serializers correspondentes.


class ManagementAssignmentViewSet(RobustModelViewSet):
    """CRUD de atribuições de gestão com joins para professor, escola e ano."""
    queryset = ManagementAssignment.objects.select_related("teacher", "school", "academic_year")
    serializer_class = ManagementAssignmentSerializer


class AnnouncementViewSet(RobustModelViewSet):
    """CRUD de comunicados com pré-carregamento de escola/turma/autor."""
    queryset = Announcement.objects.select_related("school", "classroom", "author")
    serializer_class = AnnouncementSerializer
