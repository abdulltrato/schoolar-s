from rest_framework import serializers

from core.serializers import TenantAcademicYearField
from .models import AcademicYear, Grade, GradeSubject


class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = "__all__"


class GradeSerializer(serializers.ModelSerializer):
    education_level = serializers.CharField(read_only=True)
    cycle_model_code = serializers.CharField(source="cycle_model.code", read_only=True)
    cycle_model_name = serializers.CharField(source="cycle_model.name", read_only=True)

    class Meta:
        model = Grade
        fields = [
            "id",
            "code",
            "number",
            "cycle",
            "cycle_model",
            "cycle_model_code",
            "cycle_model_name",
            "education_level",
            "name",
            "created_at",
            "updated_at",
            "deleted_at",
        ]


class GradeSubjectSerializer(serializers.ModelSerializer):
    academic_year = TenantAcademicYearField(queryset=AcademicYear.objects.all())
    grade = serializers.SlugRelatedField(slug_field="number", queryset=Grade.objects.all())
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    academic_year_code = serializers.CharField(source="academic_year.code", read_only=True)

    class Meta:
        model = GradeSubject
        fields = "__all__"
