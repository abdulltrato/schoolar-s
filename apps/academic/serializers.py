from rest_framework import serializers

from .models import Guardian, Student, StudentCompetency, StudentGuardian


class StudentCompetencySerializer(serializers.ModelSerializer):
    competency_name = serializers.CharField(source="competency.name", read_only=True)
    level = serializers.DecimalField(source="nivel", max_digits=3, decimal_places=1, read_only=True)

    class Meta:
        model = StudentCompetency
        fields = ["id", "competency", "competency_name", "level", "updated_at"]


class StudentSerializer(serializers.ModelSerializer):
    competencies = StudentCompetencySerializer(source="studentcompetency_set", many=True, read_only=True)
    cycle = serializers.IntegerField(read_only=True)
    education_level = serializers.CharField(read_only=True)
    status = serializers.CharField(source="estado")

    class Meta:
        model = Student
        fields = ["id", "user", "name", "tenant_id", "birth_date", "grade", "cycle", "education_level", "status", "competencies"]


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
