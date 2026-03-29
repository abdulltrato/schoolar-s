from core.viewsets import RobustModelViewSet
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    Assignment,
    Course,
    CourseModule,
    CourseOffering,
    Lesson,
    LessonMaterial,
    Submission,
    SubmissionAttachment,
)
from .serializers import (
    AssignmentSerializer,
    CourseOfferingSerializer,
    CourseModuleSerializer,
    CourseSerializer,
    LessonMaterialSerializer,
    LessonSerializer,
    SubmissionSerializer,
    SubmissionAttachmentSerializer,
)


class CourseViewSet(RobustModelViewSet):
    queryset = Course.objects.select_related("school").prefetch_related("modules").all()
    serializer_class = CourseSerializer
    search_fields = ("title", "description", "school__name", "tenant_id")
    ordering_fields = ("id", "tenant_id", "title", "school__name", "modality", "cycle_model__code")
    ordering = ("title",)
    allowed_roles = {
        "*": {
            "national_admin",
            "provincial_admin",
            "district_admin",
            "school_director",
            "teacher",
        },
        "list": {
            "national_admin",
            "provincial_admin",
            "district_admin",
            "school_director",
            "teacher",
            "student",
            "guardian",
        },
        "retrieve": {
            "national_admin",
            "provincial_admin",
            "district_admin",
            "school_director",
            "teacher",
            "student",
            "guardian",
        },
    }


class CourseModuleViewSet(RobustModelViewSet):
    queryset = CourseModule.objects.select_related("course", "subject").all()
    serializer_class = CourseModuleSerializer
    search_fields = ("course__title", "subject__name", "tenant_id")
    ordering_fields = ("id", "tenant_id", "course__title", "subject__name", "order", "required")
    ordering = ("course__title", "order", "subject__name")
    allowed_roles = CourseViewSet.allowed_roles


class CourseOfferingViewSet(RobustModelViewSet):
    queryset = CourseOffering.objects.select_related(
        "course", "classroom", "teacher", "academic_year"
    ).all()
    serializer_class = CourseOfferingSerializer
    search_fields = (
        "course__title",
        "classroom__name",
        "teacher__name",
        "academic_year__code",
        "tenant_id",
    )
    ordering_fields = (
        "id",
        "tenant_id",
        "course__title",
        "academic_year__code",
        "start_date",
        "end_date",
    )
    ordering = ("-academic_year__code", "course__title")
    allowed_roles = CourseViewSet.allowed_roles


class LessonViewSet(RobustModelViewSet):
    queryset = Lesson.objects.select_related("offering", "offering__course").all()
    serializer_class = LessonSerializer
    search_fields = ("title", "tenant_id", "offering__course__title")
    ordering_fields = ("id", "tenant_id", "scheduled_at", "title", "published")
    ordering = ("scheduled_at",)
    allowed_roles = CourseViewSet.allowed_roles

    @action(detail=False, methods=["get"])
    def proximas(self, request, *args, **kwargs):
        """Retorna próximas aulas a partir de agora (ordenadas asc)."""
        now = timezone.now()
        qs = self.filter_queryset(self.get_queryset().filter(scheduled_at__gte=now).order_by("scheduled_at"))
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def passadas(self, request, *args, **kwargs):
        """Retorna aulas já ocorridas (ordenadas desc)."""
        now = timezone.now()
        qs = self.filter_queryset(self.get_queryset().filter(scheduled_at__lt=now).order_by("-scheduled_at"))
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


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
    queryset = Submission.objects.select_related("assignment", "student").prefetch_related("attachments").all()
    serializer_class = SubmissionSerializer
    search_fields = ("assignment__title", "student__name", "status", "tenant_id")
    ordering_fields = ("id", "tenant_id", "submitted_at", "status", "score")
    ordering = ("-submitted_at",)
    allowed_roles = {
        "*": {
            "national_admin",
            "provincial_admin",
            "district_admin",
            "school_director",
            "teacher",
            "student",
        },
        "list": {
            "national_admin",
            "provincial_admin",
            "district_admin",
            "school_director",
            "teacher",
            "student",
            "guardian",
        },
        "retrieve": {
            "national_admin",
            "provincial_admin",
            "district_admin",
            "school_director",
            "teacher",
            "student",
            "guardian",
        },
    }


class SubmissionAttachmentViewSet(RobustModelViewSet):
    queryset = SubmissionAttachment.objects.select_related("submission", "submission__student").all()
    serializer_class = SubmissionAttachmentSerializer
    search_fields = ("title", "submission__student__name", "tenant_id")
    ordering_fields = ("id", "tenant_id", "created_at")
    ordering = ("-created_at",)
