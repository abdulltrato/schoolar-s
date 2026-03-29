from core.viewsets import RobustModelViewSet
from .models import AuditAlert, AuditEvent
from .serializers import AuditAlertSerializer, AuditEventSerializer


class AuditEventViewSet(RobustModelViewSet):
    queryset = AuditEvent.objects.all()
    serializer_class = AuditEventSerializer
    search_fields = ("resource", "username", "action")


class AuditAlertViewSet(RobustModelViewSet):
    queryset = AuditAlert.objects.all()
    serializer_class = AuditAlertSerializer
    search_fields = ("resource", "username", "severity")
