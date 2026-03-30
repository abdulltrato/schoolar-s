from rest_framework import serializers
# Base de serializers do DRF.

from core.serializers import TenantAcademicYearField
# Campo customizado para validar tenant em anos letivos.
from .models import Classroom, School, TeachingAssignment, Grade, AcademicYear
# Modelos escolares usados nas APIs.


class SchoolSerializer(serializers.ModelSerializer):
    """Serializa escolas/tenants."""

    class Meta:
        model = School
        fields = "__all__"


class ClassroomSerializer(serializers.ModelSerializer):
    """Serializa turmas com metadados derivados (trilha, códigos)."""

    grade = serializers.SlugRelatedField(slug_field="number", queryset=Grade.objects.all())
    academic_year = TenantAcademicYearField(queryset=AcademicYear.objects.all())
    grade_name = serializers.CharField(source="grade.name", read_only=True)
    school_name = serializers.CharField(source="school.name", read_only=True)
    lead_teacher_name = serializers.CharField(source="lead_teacher.name", read_only=True)
    academic_year_code = serializers.CharField(source="academic_year.code", read_only=True)
    education_track = serializers.SerializerMethodField()
    cycle_model_code = serializers.CharField(source="cycle_model.code", read_only=True)
    cycle_model_name = serializers.CharField(source="cycle_model.name", read_only=True)

    @staticmethod
    def get_education_track(obj):
        if obj.grade_id and obj.grade.number:
            return "technical" if obj.grade.number > 12 else "general"
        return None

    class Meta:
        model = Classroom
        fields = "__all__"


class TeachingAssignmentSerializer(serializers.ModelSerializer):
    """Serializa alocações docentes com campos de leitura amigáveis."""

    teacher_name = serializers.CharField(source="teacher.name", read_only=True)
    classroom_name = serializers.CharField(source="classroom.name", read_only=True)
    school_name = serializers.CharField(source="classroom.school.name", read_only=True)
    subject_name = serializers.CharField(source="grade_subject.subject.name", read_only=True)
    academic_year_code = serializers.CharField(source="grade_subject.academic_year.code", read_only=True)
    grade_number = serializers.IntegerField(source="grade_subject.grade.number", read_only=True)

    class Meta:
        model = TeachingAssignment
        fields = "__all__"
