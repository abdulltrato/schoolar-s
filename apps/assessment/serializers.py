from rest_framework import serializers

from core.serializers import TenantAcademicYearField

from .models import Assessment, AssessmentComponent, AssessmentOutcomeMap, AssessmentPeriod, SubjectPeriodResult


class AssessmentPeriodSerializer(serializers.ModelSerializer):
    academic_year = TenantAcademicYearField()
    academic_year_code = serializers.CharField(source="academic_year.code", read_only=True)

    class Meta:
        model = AssessmentPeriod
        fields = "__all__"


class AssessmentComponentSerializer(serializers.ModelSerializer):
    period_name = serializers.CharField(source="period.name", read_only=True)
    subject_name = serializers.CharField(source="grade_subject.subject.name", read_only=True)
    grade_number = serializers.IntegerField(source="grade_subject.grade.number", read_only=True)
    academic_year_code = serializers.CharField(source="grade_subject.academic_year.code", read_only=True)

    class Meta:
        model = AssessmentComponent
        fields = "__all__"


class AssessmentOutcomeMapSerializer(serializers.ModelSerializer):
    component_name = serializers.CharField(source="component.name", read_only=True)
    outcome_code = serializers.CharField(source="outcome.code", read_only=True)
    outcome_description = serializers.CharField(source="outcome.description", read_only=True)

    class Meta:
        model = AssessmentOutcomeMap
        fields = "__all__"


class AssessmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.name", read_only=True)
    competency_name = serializers.CharField(source="competency.name", read_only=True)
    teacher_name = serializers.CharField(source="teaching_assignment.teacher.name", read_only=True)
    classroom_name = serializers.CharField(source="teaching_assignment.classroom.name", read_only=True)
    subject_name = serializers.CharField(source="teaching_assignment.grade_subject.subject.name", read_only=True)
    academic_year_code = serializers.CharField(source="teaching_assignment.classroom.academic_year.code", read_only=True)
    grade_number = serializers.IntegerField(source="teaching_assignment.classroom.grade.number", read_only=True)
    period_name = serializers.CharField(source="period.name", read_only=True)
    component_name = serializers.CharField(source="component.name", read_only=True)

    class Meta:
        model = Assessment
        fields = "__all__"


class SubjectPeriodResultSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.name", read_only=True)
    teacher_name = serializers.CharField(source="teaching_assignment.teacher.name", read_only=True)
    classroom_name = serializers.CharField(source="teaching_assignment.classroom.name", read_only=True)
    subject_name = serializers.CharField(source="teaching_assignment.grade_subject.subject.name", read_only=True)
    period_name = serializers.CharField(source="period.name", read_only=True)

    class Meta:
        model = SubjectPeriodResult
        fields = "__all__"
