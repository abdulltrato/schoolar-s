from rest_framework import serializers

from .models import (
    Guardian,
    Student,
    StudentCompetency,
    StudentGuardian,
    StudentOutcome,
)


class StudentCompetencySerializer(serializers.ModelSerializer):
    competency_name = serializers.CharField(source="competency.name", read_only=True)
    level = serializers.DecimalField(
        source="nivel", max_digits=3, decimal_places=1, read_only=True
    )

    class Meta:
        model = StudentCompetency
        fields = ["id", "code", "competency", "competency_name", "level", "updated_at"]


class StudentOutcomeSerializer(serializers.ModelSerializer):
    outcome_code = serializers.CharField(source="outcome.code", read_only=True)
    outcome_description = serializers.CharField(
        source="outcome.description", read_only=True
    )
    taxonomy_level = serializers.CharField(
        source="outcome.taxonomy_level", read_only=True
    )
    knowledge_dimension = serializers.CharField(
        source="outcome.knowledge_dimension", read_only=True
    )

    class Meta:
        model = StudentOutcome
        fields = "__all__"


class StudentSerializer(serializers.ModelSerializer):
    competencies = StudentCompetencySerializer(
        source="studentcompetency_set", many=True, read_only=True
    )
    outcomes = StudentOutcomeSerializer(
        source="studentoutcome_set", many=True, read_only=True
    )
    cycle = serializers.IntegerField(read_only=True)
    education_level = serializers.CharField(read_only=True)
    status = serializers.CharField(source="estado")

    class Meta:
        model = Student
        fields = [
            "id",
            "code",
            "user",
            "name",
            "tenant_id",
            "birth_date",
            "grade",
            "cycle",
            "education_level",
            "status",
            "competencies",
            "outcomes",
            "created_at",
            "updated_at",
            "deleted_at",
        ]


class GuardianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guardian
        fields = "__all__"


class StudentGuardianSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.name", read_only=True)
    guardian_name = serializers.CharField(source="guardian.name", read_only=True)

    class Meta:
        model = StudentGuardian
        fields = "__all__"
