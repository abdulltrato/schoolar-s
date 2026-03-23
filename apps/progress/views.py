from core.viewsets import RobustModelViewSet

from .models import Progression
from .serializers import ProgressionSerializer


class ProgressionViewSet(RobustModelViewSet):
    queryset = Progression.objects.select_related("student").all()
    serializer_class = ProgressionSerializer
    search_fields = ("student__name", "academic_year", "decision")
    ordering_fields = ("id", "decision_date", "academic_year", "decision")
    ordering = ("-decision_date",)
