from rest_framework import serializers

from .models import AuditAlert, AuditEvent


class AuditEventSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(read_only=True)

    class Meta:
        model = AuditEvent
        fields = "__all__"
        read_only_fields = ("tenant_name",)


class AuditAlertSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(read_only=True)

    class Meta:
        model = AuditAlert
        fields = "__all__"
        read_only_fields = ("tenant_name",)
