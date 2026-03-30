from rest_framework import serializers
# Base de serializers do DRF.

from .models import AuditAlert, AuditEvent
# Modelos de auditoria.


class AuditEventSerializer(serializers.ModelSerializer):
    """Serializa eventos de auditoria, incluindo nome do tenant calculado."""

    tenant_name = serializers.CharField(read_only=True)

    class Meta:
        model = AuditEvent
        fields = "__all__"
        read_only_fields = ("tenant_name",)


class AuditAlertSerializer(serializers.ModelSerializer):
    """Serializa alertas de auditoria, incluindo nome do tenant calculado."""

    tenant_name = serializers.CharField(read_only=True)

    class Meta:
        model = AuditAlert
        fields = "__all__"
        read_only_fields = ("tenant_name",)
