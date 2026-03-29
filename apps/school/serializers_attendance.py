from rest_framework import serializers

from .models import AttendanceRecord


class AttendanceRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="enrollment.student.name", read_only=True)
    classroom_name = serializers.CharField(source="enrollment.classroom.name", read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = "__all__"
