from rest_framework import serializers
# Base de serializers do DRF.

from .models import Transfer
# Modelo de transferência.


class TransferSerializer(serializers.ModelSerializer):
    """Serializa transferências; status/códigos são somente leitura."""
    class Meta:
        model = Transfer
        fields = "__all__"
        read_only_fields = ("status", "applied_at", "error_message", "tenant_id", "code", "custom_id", "usuario")
