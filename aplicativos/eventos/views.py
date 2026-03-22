from .models import Evento
from .serializers import EventoSerializer
from nucleo.viewsets import RobustModelViewSet

class EventoViewSet(RobustModelViewSet):
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer
    search_fields = ("tipo", "tenant_id")
    ordering_fields = ("id", "tipo", "tenant_id", "data")
    ordering = ("-data",)
