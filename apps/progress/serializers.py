from rest_framework import serializers
# Base de serializers do DRF.

from .models import Progression
# Modelo de progressão.


class ProgressionSerializer(serializers.ModelSerializer):
    """Serializa progressões incluindo o nome do aluno para leitura."""

    student_name = serializers.CharField(source="student.name", read_only=True)

    class Meta:
        model = Progression
        fields = "__all__"
