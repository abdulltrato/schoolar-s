from core.viewsets import RobustModelViewSet
# ViewSet base com tratamento robusto de erros.
from .models import AuditAlert, AuditEvent
# Modelos de auditoria.
from .serializers import AuditAlertSerializer, AuditEventSerializer
# Serializers correspondentes.


class AuditEventViewSet(RobustModelViewSet):
    """CRUD de eventos de auditoria; busca por recurso, usuário ou ação."""
    queryset = AuditEvent.objects.all()
    serializer_class = AuditEventSerializer
    search_fields = ("resource", "username", "action")


class AuditAlertViewSet(RobustModelViewSet):
    """CRUD de alertas de auditoria; busca por recurso, usuário ou severidade."""
    queryset = AuditAlert.objects.all()
    serializer_class = AuditAlertSerializer
    search_fields = ("resource", "username", "severity")
