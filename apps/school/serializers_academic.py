from rest_framework import serializers
# Base de serializers do DRF.

from core.serializers import TenantAcademicYearField
# Campo custom para aplicar tenant ao ano letivo.
from .models import AcademicYear, Grade, GradeSubject
# Modelos acadêmicos da app school.


class AcademicYearSerializer(serializers.ModelSerializer):
    """Serializa anos letivos garantindo deleted_at padrão."""

    def to_internal_value(self, data):
        mutable = data.copy()
        mutable.setdefault("deleted_at", None)
        return super().to_internal_value(mutable)

    def validate(self, attrs):
        attrs.setdefault("deleted_at", None)
        return super().validate(attrs)

    class Meta:
        model = AcademicYear
        fields = "__all__"


class GradeSerializer(serializers.ModelSerializer):
    """Serializa classes exibindo nível educacional e dados do cycle_model."""

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
    """Serializa oferta de disciplina por classe/ano letivo."""

    academic_year = TenantAcademicYearField(queryset=AcademicYear.objects.all())
    grade = serializers.SlugRelatedField(slug_field="number", queryset=Grade.objects.all())
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    academic_year_code = serializers.CharField(source="academic_year.code", read_only=True)

    class Meta:
        model = GradeSubject
        fields = "__all__"
