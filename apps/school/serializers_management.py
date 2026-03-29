from rest_framework import serializers

from core.serializers import TenantAcademicYearField
from .models import AcademicYear, ManagementAssignment


class ManagementAssignmentSerializer(serializers.ModelSerializer):
    academic_year = TenantAcademicYearField(queryset=AcademicYear.objects.all())
    teacher_name = serializers.CharField(source="teacher.name", read_only=True)
    school_name = serializers.CharField(source="school.name", read_only=True)
    academic_year_code = serializers.CharField(source="academic_year.code", read_only=True)
    grade_number = serializers.IntegerField(source="grade.number", read_only=True)
    classroom_name = serializers.CharField(source="classroom.name", read_only=True)

    class Meta:
        model = ManagementAssignment
        fields = "__all__"
