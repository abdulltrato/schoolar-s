from rest_framework import serializers

from .models import Event


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"

    def to_internal_value(self, data):
        normalized = data.copy()
        if "tipo" in normalized and "type" not in normalized:
            normalized["type"] = normalized["tipo"]
        if "dados" in normalized and "payload" not in normalized:
            normalized["payload"] = normalized["dados"]
        if "type" in normalized:
            normalized["type"] = Event.LEGACY_TYPE_MAP.get(normalized["type"], normalized["type"])
        return super().to_internal_value(normalized)
