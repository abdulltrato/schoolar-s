from core.viewsets import RobustModelViewSet

from .models import Event
from .serializers import EventSerializer


class EventViewSet(RobustModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    search_fields = ("type", "tenant_id")
    ordering_fields = ("id", "type", "tenant_id", "created_at")
    ordering = ("-created_at",)
