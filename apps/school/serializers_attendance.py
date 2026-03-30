from rest_framework import serializers
# Base de serializers do DRF.

from .models import AttendanceRecord
# Modelo de registro de presença.


class AttendanceRecordSerializer(serializers.ModelSerializer):
    """Serializa presenças exibindo aluno e turma derivados da matrícula."""

    student_name = serializers.CharField(source="enrollment.student.name", read_only=True)
    classroom_name = serializers.CharField(source="enrollment.classroom.name", read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = "__all__"
