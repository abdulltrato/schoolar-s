from core.viewsets import RobustModelViewSet

from .models import Report
from .serializers import ReportSerializer


class ReportViewSet(RobustModelViewSet):
    queryset = Report.objects.select_related("student").all()
    serializer_class = ReportSerializer
    search_fields = ("title", "type", "period", "student__name")
    ordering_fields = ("id", "title", "type", "period", "generated_at")
    ordering = ("-generated_at",)
