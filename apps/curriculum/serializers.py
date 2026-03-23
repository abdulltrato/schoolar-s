from rest_framework import serializers

from apps.school.models import Grade

from .models import (
    BaseCurriculum,
    Competency,
    CompetencyOutcome,
    CurriculumArea,
    LearningOutcome,
    LocalCurriculum,
    Subject,
    SubjectCurriculumPlan,
)


class CurriculumAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurriculumArea
        fields = "__all__"


class SubjectSerializer(serializers.ModelSerializer):
    area = CurriculumAreaSerializer(read_only=True)
    area_id = serializers.PrimaryKeyRelatedField(source="area", queryset=CurriculumArea.objects.all(), write_only=True)

    class Meta:
        model = Subject
        fields = "__all__"


class CompetencySerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    subject_id = serializers.PrimaryKeyRelatedField(
        source="subject",
        queryset=Subject.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    grade = serializers.PrimaryKeyRelatedField(queryset=Grade.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Competency
        fields = "__all__"


class BaseCurriculumSerializer(serializers.ModelSerializer):
    competencies = CompetencySerializer(many=True, read_only=True)
    competency_ids = serializers.PrimaryKeyRelatedField(
        source="competencies",
        queryset=Competency.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )

    class Meta:
        model = BaseCurriculum
        fields = "__all__"

    def to_internal_value(self, data):
        normalized = data.copy()
        if "competencia_ids" in normalized and "competency_ids" not in normalized:
            normalized["competency_ids"] = normalized["competencia_ids"]
        return super().to_internal_value(normalized)


class LocalCurriculumSerializer(serializers.ModelSerializer):
    additional_competencies = CompetencySerializer(many=True, read_only=True)
    competency_ids = serializers.PrimaryKeyRelatedField(
        source="additional_competencies",
        queryset=Competency.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )

    class Meta:
        model = LocalCurriculum
        fields = "__all__"

    def to_internal_value(self, data):
        normalized = data.copy()
        if "competencia_ids" in normalized and "competency_ids" not in normalized:
            normalized["competency_ids"] = normalized["competencia_ids"]
        return super().to_internal_value(normalized)


class SubjectCurriculumPlanSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="grade_subject.subject.name", read_only=True)
    grade_number = serializers.IntegerField(source="grade_subject.grade.number", read_only=True)
    academic_year_code = serializers.CharField(source="grade_subject.academic_year.code", read_only=True)
    planned_competencies = CompetencySerializer(many=True, read_only=True)
    competency_ids = serializers.PrimaryKeyRelatedField(
        source="planned_competencies",
        queryset=Competency.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )

    class Meta:
        model = SubjectCurriculumPlan
        fields = "__all__"

    def to_internal_value(self, data):
        normalized = data.copy()
        if "competencia_ids" in normalized and "competency_ids" not in normalized:
            normalized["competency_ids"] = normalized["competencia_ids"]
        return super().to_internal_value(normalized)


class LearningOutcomeSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    grade_number = serializers.IntegerField(source="grade.number", read_only=True)

    class Meta:
        model = LearningOutcome
        fields = "__all__"


class CompetencyOutcomeSerializer(serializers.ModelSerializer):
    competency_name = serializers.CharField(source="competency.name", read_only=True)
    outcome_code = serializers.CharField(source="outcome.code", read_only=True)
    outcome_description = serializers.CharField(source="outcome.description", read_only=True)

    class Meta:
        model = CompetencyOutcome
        fields = "__all__"
