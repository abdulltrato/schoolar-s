from rest_framework import serializers

from .models import Progression


class ProgressionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.name", read_only=True)

    class Meta:
        model = Progression
        fields = "__all__"
