from rest_framework import serializers

from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    titulo = serializers.CharField(source="title", write_only=True, required=False)
    tipo = serializers.CharField(source="type", write_only=True, required=False)
    conteudo = serializers.JSONField(source="content", write_only=True, required=False)

    class Meta:
        model = Report
        fields = "__all__"
