from core.viewsets import RobustModelViewSet

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
from .serializers import (
    BaseCurriculumSerializer,
    CompetencySerializer,
    CompetencyOutcomeSerializer,
    CurriculumAreaSerializer,
    LearningOutcomeSerializer,
    LocalCurriculumSerializer,
    SubjectCurriculumPlanSerializer,
    SubjectSerializer,
)


class CurriculumAreaViewSet(RobustModelViewSet):
    queryset = CurriculumArea.objects.all()
    serializer_class = CurriculumAreaSerializer
    search_fields = ("name",)
    ordering_fields = ("id", "name")
    ordering = ("name",)


class SubjectViewSet(RobustModelViewSet):
    queryset = Subject.objects.select_related("area").all()
    serializer_class = SubjectSerializer
    search_fields = ("name", "area__name")
    ordering_fields = ("id", "name", "cycle", "area__name")
    ordering = ("name",)


class CompetencyViewSet(RobustModelViewSet):
    queryset = Competency.objects.select_related("subject", "subject__area").all()
    serializer_class = CompetencySerializer
    search_fields = ("name", "area", "subject__name")
    ordering_fields = ("id", "name", "cycle", "area")
    ordering = ("name",)


class BaseCurriculumViewSet(RobustModelViewSet):
    queryset = BaseCurriculum.objects.prefetch_related("competencies").all()
    serializer_class = BaseCurriculumSerializer
    ordering_fields = ("id", "cycle")
    ordering = ("cycle",)


class LocalCurriculumViewSet(RobustModelViewSet):
    queryset = LocalCurriculum.objects.prefetch_related("additional_competencies").all()
    serializer_class = LocalCurriculumSerializer
    search_fields = ("tenant_id",)
    ordering_fields = ("id", "tenant_id", "cycle")
    ordering = ("tenant_id", "cycle")


class SubjectCurriculumPlanViewSet(RobustModelViewSet):
    queryset = SubjectCurriculumPlan.objects.select_related(
        "grade_subject",
        "grade_subject__academic_year",
        "grade_subject__grade",
        "grade_subject__subject",
    ).prefetch_related("planned_competencies").all()
    serializer_class = SubjectCurriculumPlanSerializer
    search_fields = (
        "grade_subject__academic_year__code",
        "grade_subject__grade__name",
        "grade_subject__subject__name",
    )
    ordering_fields = (
        "id",
        "grade_subject__academic_year__code",
        "grade_subject__grade__number",
        "grade_subject__subject__name",
    )
    ordering = ("grade_subject__academic_year__code", "grade_subject__grade__number")


class LearningOutcomeViewSet(RobustModelViewSet):
    queryset = LearningOutcome.objects.select_related("subject", "grade").all()
    serializer_class = LearningOutcomeSerializer
    search_fields = ("code", "description", "tenant_id", "subject__name")
    ordering_fields = ("id", "code", "taxonomy_level", "cycle", "tenant_id")
    ordering = ("code",)


class CompetencyOutcomeViewSet(RobustModelViewSet):
    queryset = CompetencyOutcome.objects.select_related("competency", "outcome").all()
    serializer_class = CompetencyOutcomeSerializer
    search_fields = ("competency__name", "outcome__code", "tenant_id")
    ordering_fields = ("id", "weight", "tenant_id")
    ordering = ("-weight",)
