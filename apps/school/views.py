import csv

from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response

from core.viewsets import RobustModelViewSet

from .models import (
    AcademicYear,
    AuditAlert,
    AuditEvent,
    Announcement,
    AttendanceRecord,
    Classroom,
    Enrollment,
    Grade,
    GradeSubject,
    Invoice,
    ManagementAssignment,
    Payment,
    School,
    Teacher,
    TeachingAssignment,
    UserProfile,
)
from .serializers import (
    AcademicYearSerializer,
    AuditAlertSerializer,
    AuditEventSerializer,
    AnnouncementSerializer,
    AttendanceRecordSerializer,
    ClassroomSerializer,
    EnrollmentSerializer,
    GradeSerializer,
    GradeSubjectSerializer,
    InvoiceSerializer,
    ManagementAssignmentSerializer,
    PaymentSerializer,
    SchoolSerializer,
    TeacherSerializer,
    TeachingAssignmentSerializer,
    UserProfileSerializer,
)


class AcademicYearViewSet(RobustModelViewSet):
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    search_fields = ("code",)
    ordering_fields = ("id", "code", "start_date", "end_date", "active")
    ordering = ("-code",)
    allowed_roles = {
        "*": {"national_admin", "provincial_admin", "district_admin", "school_director"},
        "list": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher", "student", "guardian", "finance_officer"},
        "retrieve": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher", "student", "guardian", "finance_officer"},
    }


class AuditEventViewSet(RobustModelViewSet):
    queryset = AuditEvent.objects.all()
    serializer_class = AuditEventSerializer
    search_fields = ("resource", "action", "tenant_id", "username", "request_id", "path")
    ordering_fields = ("id", "resource", "action", "tenant_id", "username", "created_at")
    ordering = ("-created_at",)
    allowed_roles = {
        "*": {"national_admin", "provincial_admin", "district_admin"},
        "list": {"national_admin", "provincial_admin", "district_admin", "school_director", "support"},
        "retrieve": {"national_admin", "provincial_admin", "district_admin", "school_director", "support"},
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params

        resource = params.get("resource")
        action_name = params.get("action")
        username = params.get("username")
        tenant_id = params.get("tenant_id")
        date_from = params.get("date_from")
        date_to = params.get("date_to")

        if resource:
            queryset = queryset.filter(resource=resource)
        if action_name:
            queryset = queryset.filter(action=action_name)
        if username:
            queryset = queryset.filter(username=username)
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)

        return queryset

    @action(detail=False, methods=["get"], url_path="exports/download")
    def export(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        export_format = request.query_params.get("export_format", "csv").lower()

        if export_format == "json":
            serializer = self.get_serializer(queryset, many=True)
            return HttpResponse(
                self.renderer_classes[0]().render(serializer.data),
                content_type="application/json",
                headers={"Content-Disposition": 'attachment; filename="audit-events.json"'},
            )

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="audit-events.csv"'
        writer = csv.writer(response)
        writer.writerow([
            "id",
            "resource",
            "action",
            "object_id",
            "tenant_id",
            "username",
            "role",
            "method",
            "path",
            "request_id",
            "changed_fields",
            "created_at",
        ])
        for event in queryset:
            writer.writerow([
                event.id,
                event.resource,
                event.action,
                event.object_id,
                event.tenant_id,
                event.username,
                event.role,
                event.method,
                event.path,
                event.request_id,
                ",".join(event.changed_fields or []),
                event.created_at.isoformat(),
            ])
        return response


class AuditAlertViewSet(RobustModelViewSet):
    queryset = AuditAlert.objects.all()
    serializer_class = AuditAlertSerializer
    search_fields = ("alert_type", "severity", "tenant_id", "resource", "username", "summary")
    ordering_fields = ("id", "alert_type", "severity", "tenant_id", "username", "created_at", "acknowledged")
    ordering = ("-created_at",)
    allowed_roles = {
        "*": {"national_admin", "provincial_admin", "district_admin"},
        "list": {"national_admin", "provincial_admin", "district_admin", "school_director", "support"},
        "retrieve": {"national_admin", "provincial_admin", "district_admin", "school_director", "support"},
        "update": {"national_admin", "provincial_admin", "district_admin", "school_director", "support"},
        "partial_update": {"national_admin", "provincial_admin", "district_admin", "school_director", "support"},
        "acknowledge": {"national_admin", "provincial_admin", "district_admin", "school_director", "support"},
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params

        severity = params.get("severity")
        acknowledged = params.get("acknowledged")
        username = params.get("username")
        tenant_id = params.get("tenant_id")
        resource = params.get("resource")
        date_from = params.get("date_from")
        date_to = params.get("date_to")

        if severity:
            queryset = queryset.filter(severity=severity)
        if acknowledged in {"true", "false"}:
            queryset = queryset.filter(acknowledged=acknowledged == "true")
        if username:
            queryset = queryset.filter(username=username)
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        if resource:
            queryset = queryset.filter(resource=resource)
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)

        return queryset

    @action(detail=True, methods=["post"], url_path="acknowledge")
    def acknowledge(self, request, pk=None):
        alert = self.get_object()
        if not alert.acknowledged:
            alert.acknowledged = True
            alert.save(update_fields=["acknowledged"])
        serializer = self.get_serializer(alert)
        return Response(serializer.data)


class GradeViewSet(RobustModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    search_fields = ("number", "name")
    ordering_fields = ("id", "number", "cycle", "name")
    ordering = ("number",)
    allowed_roles = AcademicYearViewSet.allowed_roles


class SchoolViewSet(RobustModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    search_fields = ("code", "name", "district", "province")
    ordering_fields = ("id", "code", "name", "district", "province")
    ordering = ("name",)
    allowed_roles = AcademicYearViewSet.allowed_roles


class TeacherViewSet(RobustModelViewSet):
    queryset = Teacher.objects.select_related("school").all()
    serializer_class = TeacherSerializer
    search_fields = ("name", "specialty__name", "user__username", "school__name", "tenant_id")
    ordering_fields = ("id", "name", "tenant_id", "specialty__name", "school__name")
    ordering = ("name",)
    allowed_roles = {
        "*": {"national_admin", "provincial_admin", "district_admin", "school_director"},
        "list": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher"},
        "retrieve": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher"},
    }


class ClassroomViewSet(RobustModelViewSet):
    queryset = Classroom.objects.select_related("school", "grade", "academic_year", "lead_teacher").all()
    serializer_class = ClassroomSerializer
    search_fields = ("name", "tenant_id", "academic_year__code", "grade__name", "lead_teacher__name", "school__name")
    ordering_fields = ("id", "name", "tenant_id", "cycle", "academic_year__code", "grade__number", "school__name")
    ordering = ("academic_year__code", "grade__number", "name")
    allowed_roles = {
        "*": {"national_admin", "provincial_admin", "district_admin", "school_director"},
        "list": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher", "student", "guardian"},
        "retrieve": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher", "student", "guardian"},
    }


class GradeSubjectViewSet(RobustModelViewSet):
    queryset = GradeSubject.objects.select_related("academic_year", "grade", "subject").all()
    serializer_class = GradeSubjectSerializer
    search_fields = ("academic_year__code", "grade__name", "subject__name")
    ordering_fields = ("id", "academic_year__code", "grade__number", "subject__name")
    ordering = ("academic_year__code", "grade__number", "subject__name")
    allowed_roles = ClassroomViewSet.allowed_roles


class TeachingAssignmentViewSet(RobustModelViewSet):
    queryset = TeachingAssignment.objects.select_related(
        "teacher",
        "teacher__school",
        "classroom",
        "classroom__school",
        "classroom__academic_year",
        "classroom__grade",
        "grade_subject",
        "grade_subject__subject",
    ).all()
    serializer_class = TeachingAssignmentSerializer
    search_fields = ("teacher__name", "tenant_id", "classroom__name", "grade_subject__subject__name", "classroom__school__name")
    ordering_fields = ("id", "tenant_id", "teacher__name", "classroom__name", "grade_subject__subject__name")
    ordering = ("classroom__academic_year__code", "classroom__grade__number", "classroom__name")
    allowed_roles = {
        "*": {"national_admin", "provincial_admin", "district_admin", "school_director"},
        "list": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher"},
        "retrieve": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher"},
    }


class EnrollmentViewSet(RobustModelViewSet):
    queryset = Enrollment.objects.select_related(
        "student",
        "classroom",
        "classroom__school",
        "classroom__academic_year",
        "classroom__grade",
    ).all()
    serializer_class = EnrollmentSerializer
    search_fields = ("student__name", "tenant_id", "classroom__name", "classroom__academic_year__code", "classroom__school__name")
    ordering_fields = ("id", "tenant_id", "enrollment_date", "student__name", "classroom__name")
    ordering = ("-enrollment_date",)
    allowed_roles = {
        "*": {"national_admin", "provincial_admin", "district_admin", "school_director"},
        "list": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher", "student", "guardian"},
        "retrieve": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher", "student", "guardian"},
    }


class ManagementAssignmentViewSet(RobustModelViewSet):
    queryset = ManagementAssignment.objects.select_related(
        "teacher",
        "teacher__school",
        "school",
        "academic_year",
        "grade",
        "classroom",
    ).all()
    serializer_class = ManagementAssignmentSerializer
    search_fields = ("teacher__name", "tenant_id", "school__name", "role", "academic_year__code")
    ordering_fields = ("id", "tenant_id", "teacher__name", "school__name", "role", "academic_year__code")
    ordering = ("academic_year__code", "school__name", "role")
    allowed_roles = {
        "*": {"national_admin", "provincial_admin", "district_admin", "school_director"},
        "list": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher"},
        "retrieve": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher"},
    }


class UserProfileViewSet(RobustModelViewSet):
    queryset = UserProfile.objects.select_related("user", "school").all()
    serializer_class = UserProfileSerializer
    search_fields = ("user__username", "role", "school__name", "tenant_id")
    ordering_fields = ("id", "user__username", "role", "school__name")
    ordering = ("user__username",)
    allowed_roles = {
        "*": {"national_admin", "provincial_admin", "district_admin"},
        "list": {"national_admin", "provincial_admin", "district_admin", "school_director"},
        "retrieve": {"national_admin", "provincial_admin", "district_admin", "school_director"},
    }


class AttendanceRecordViewSet(RobustModelViewSet):
    queryset = AttendanceRecord.objects.select_related(
        "enrollment",
        "enrollment__student",
        "enrollment__classroom",
    ).all()
    serializer_class = AttendanceRecordSerializer
    search_fields = ("enrollment__student__name", "tenant_id", "enrollment__classroom__name", "status")
    ordering_fields = ("id", "tenant_id", "lesson_date", "status", "enrollment__student__name")
    ordering = ("-lesson_date",)
    audit_resource = "attendance_record"
    allowed_roles = {
        "*": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher"},
        "list": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher", "student", "guardian"},
        "retrieve": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher", "student", "guardian"},
    }


class AnnouncementViewSet(RobustModelViewSet):
    queryset = Announcement.objects.select_related("school", "classroom", "author").all()
    serializer_class = AnnouncementSerializer
    search_fields = ("title", "tenant_id", "message", "audience", "school__name", "classroom__name")
    ordering_fields = ("id", "tenant_id", "published_at", "title", "audience")
    ordering = ("-published_at",)
    audit_resource = "announcement"
    allowed_roles = {
        "*": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher"},
        "list": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher", "student", "guardian", "finance_officer"},
        "retrieve": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher", "student", "guardian", "finance_officer"},
    }


class InvoiceViewSet(RobustModelViewSet):
    queryset = Invoice.objects.select_related("student", "school").all()
    serializer_class = InvoiceSerializer
    search_fields = ("reference", "tenant_id", "description", "student__name", "school__name", "status")
    ordering_fields = ("id", "tenant_id", "reference", "amount", "due_date", "status")
    ordering = ("-issued_at",)
    audit_resource = "invoice"
    allowed_roles = {
        "*": {"national_admin", "provincial_admin", "district_admin", "school_director", "finance_officer"},
        "list": {"national_admin", "provincial_admin", "district_admin", "school_director", "finance_officer", "student", "guardian"},
        "retrieve": {"national_admin", "provincial_admin", "district_admin", "school_director", "finance_officer", "student", "guardian"},
    }


class PaymentViewSet(RobustModelViewSet):
    queryset = Payment.objects.select_related("invoice").all()
    serializer_class = PaymentSerializer
    search_fields = ("invoice__reference", "tenant_id", "method", "reference")
    ordering_fields = ("id", "tenant_id", "payment_date", "amount", "method")
    ordering = ("-payment_date",)
    audit_resource = "payment"
    allowed_roles = {
        "*": {"national_admin", "provincial_admin", "district_admin", "school_director", "finance_officer"},
        "list": {"national_admin", "provincial_admin", "district_admin", "school_director", "finance_officer", "student", "guardian"},
        "retrieve": {"national_admin", "provincial_admin", "district_admin", "school_director", "finance_officer", "student", "guardian"},
    }
