from core.viewsets import RobustModelViewSet

from .models import Assessment, AssessmentComponent, AssessmentPeriod, SubjectPeriodResult
from .serializers import (
    AssessmentComponentSerializer,
    AssessmentPeriodSerializer,
    AssessmentSerializer,
    SubjectPeriodResultSerializer,
)


class AssessmentPeriodViewSet(RobustModelViewSet):
    queryset = AssessmentPeriod.objects.select_related("academic_year").all()
    serializer_class = AssessmentPeriodSerializer
    search_fields = ("name", "academic_year__code")
    ordering_fields = ("id", "academic_year__code", "order", "name")
    ordering = ("academic_year__code", "order")
    allowed_roles = {
        "*": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher"},
        "list": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher", "student", "guardian"},
        "retrieve": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher", "student", "guardian"},
    }


class AssessmentComponentViewSet(RobustModelViewSet):
    queryset = AssessmentComponent.objects.select_related(
        "period",
        "period__academic_year",
        "grade_subject",
        "grade_subject__grade",
        "grade_subject__subject",
    ).all()
    serializer_class = AssessmentComponentSerializer
    search_fields = ("name", "type", "period__name", "grade_subject__subject__name")
    ordering_fields = ("id", "period__order", "grade_subject__subject__name", "name", "weight")
    ordering = ("period__academic_year__code", "period__order", "grade_subject__subject__name")
    allowed_roles = AssessmentPeriodViewSet.allowed_roles


class AssessmentViewSet(RobustModelViewSet):
    queryset = Assessment.objects.select_related(
        "student",
        "competency",
        "period",
        "component",
        "teaching_assignment",
        "teaching_assignment__teacher",
        "teaching_assignment__classroom",
        "teaching_assignment__classroom__academic_year",
        "teaching_assignment__classroom__grade",
        "teaching_assignment__grade_subject",
        "teaching_assignment__grade_subject__subject",
    ).all()
    serializer_class = AssessmentSerializer
    search_fields = (
        "student__name",
        "tenant_id",
        "competency__name",
        "type",
        "period__name",
        "component__name",
        "teaching_assignment__grade_subject__subject__name",
        "teaching_assignment__classroom__name",
    )
    ordering_fields = ("id", "tenant_id", "date", "type", "student__name", "teaching_assignment__classroom__name", "period__order")
    ordering = ("-date",)
    audit_resource = "assessment"
    allowed_roles = {
        "*": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher"},
        "list": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher", "student", "guardian"},
        "retrieve": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher", "student", "guardian"},
    }


class SubjectPeriodResultViewSet(RobustModelViewSet):
    queryset = SubjectPeriodResult.objects.select_related(
        "student",
        "period",
        "period__academic_year",
        "teaching_assignment",
        "teaching_assignment__teacher",
        "teaching_assignment__classroom",
        "teaching_assignment__grade_subject",
        "teaching_assignment__grade_subject__subject",
    ).all()
    serializer_class = SubjectPeriodResultSerializer
    search_fields = ("student__name", "period__name", "teaching_assignment__grade_subject__subject__name")
    ordering_fields = ("id", "final_average", "period__order", "student__name")
    ordering = ("period__academic_year__code", "period__order", "student__name")
    allowed_roles = {
        "*": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher"},
        "list": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher", "student", "guardian"},
        "retrieve": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher", "student", "guardian"},
    }
