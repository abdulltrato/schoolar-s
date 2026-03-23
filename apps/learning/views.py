from core.viewsets import RobustModelViewSet

from .models import Assignment, Course, CourseOffering, Lesson, LessonMaterial, Submission
from .serializers import (
    AssignmentSerializer,
    CourseOfferingSerializer,
    CourseSerializer,
    LessonMaterialSerializer,
    LessonSerializer,
    SubmissionSerializer,
)


class CourseViewSet(RobustModelViewSet):
    queryset = Course.objects.select_related("school").all()
    serializer_class = CourseSerializer
    search_fields = ("title", "description", "school__name", "tenant_id")
    ordering_fields = ("id", "tenant_id", "title", "school__name", "modality")
    ordering = ("title",)
    allowed_roles = {
        "*": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher"},
        "list": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher", "student", "guardian"},
        "retrieve": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher", "student", "guardian"},
    }


class CourseOfferingViewSet(RobustModelViewSet):
    queryset = CourseOffering.objects.select_related("course", "classroom", "teacher", "academic_year").all()
    serializer_class = CourseOfferingSerializer
    search_fields = ("course__title", "classroom__name", "teacher__name", "academic_year__code", "tenant_id")
    ordering_fields = ("id", "tenant_id", "course__title", "academic_year__code", "start_date", "end_date")
    ordering = ("-academic_year__code", "course__title")
    allowed_roles = CourseViewSet.allowed_roles


class LessonViewSet(RobustModelViewSet):
    queryset = Lesson.objects.select_related("offering", "offering__course").all()
    serializer_class = LessonSerializer
    search_fields = ("title", "tenant_id", "offering__course__title")
    ordering_fields = ("id", "tenant_id", "scheduled_at", "title", "published")
    ordering = ("scheduled_at",)
    allowed_roles = CourseViewSet.allowed_roles


class LessonMaterialViewSet(RobustModelViewSet):
    queryset = LessonMaterial.objects.select_related("lesson").all()
    serializer_class = LessonMaterialSerializer
    search_fields = ("title", "material_type", "lesson__title")
    ordering_fields = ("id", "title", "material_type")
    ordering = ("lesson__scheduled_at", "title")
    allowed_roles = CourseViewSet.allowed_roles


class AssignmentViewSet(RobustModelViewSet):
    queryset = Assignment.objects.select_related("offering", "offering__course").all()
    serializer_class = AssignmentSerializer
    search_fields = ("title", "offering__course__title", "tenant_id")
    ordering_fields = ("id", "tenant_id", "title", "opens_at", "due_at", "published")
    ordering = ("-due_at",)
    allowed_roles = CourseViewSet.allowed_roles


class SubmissionViewSet(RobustModelViewSet):
    queryset = Submission.objects.select_related("assignment", "student").all()
    serializer_class = SubmissionSerializer
    search_fields = ("assignment__title", "student__name", "status", "tenant_id")
    ordering_fields = ("id", "tenant_id", "submitted_at", "status", "score")
    ordering = ("-submitted_at",)
    allowed_roles = {
        "*": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher", "student"},
        "list": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher", "student", "guardian"},
        "retrieve": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher", "student", "guardian"},
    }
