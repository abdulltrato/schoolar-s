from rest_framework import serializers

from .models import Transfer


class TransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfer
        fields = "__all__"
        read_only_fields = ("status", "applied_at", "error_message", "tenant_id", "code", "custom_id", "usuario")

