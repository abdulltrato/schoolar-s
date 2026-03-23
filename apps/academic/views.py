from core.viewsets import RobustModelViewSet

from .models import Guardian, Student, StudentGuardian, StudentOutcome
from .serializers import (
    GuardianSerializer,
    StudentGuardianSerializer,
    StudentOutcomeSerializer,
    StudentSerializer,
)


class StudentViewSet(RobustModelViewSet):
    queryset = Student.objects.prefetch_related(
        "studentcompetency_set__competency",
        "studentoutcome_set__outcome",
    ).all()
    serializer_class = StudentSerializer
    search_fields = ("name", "estado", "tenant_id")
    ordering_fields = ("id", "name", "tenant_id", "grade", "cycle", "birth_date")
    ordering = ("name",)
    allowed_roles = {
        "*": {
            "national_admin",
            "provincial_admin",
            "district_admin",
            "school_director",
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


class GuardianViewSet(RobustModelViewSet):
    queryset = Guardian.objects.all()
    serializer_class = GuardianSerializer
    search_fields = ("name", "tenant_id", "phone", "email", "relationship")
    ordering_fields = ("id", "name", "tenant_id", "relationship", "active")
    ordering = ("name",)
    allowed_roles = {
        "*": {
            "national_admin",
            "provincial_admin",
            "district_admin",
            "school_director",
        },
        "list": {
            "national_admin",
            "provincial_admin",
            "district_admin",
            "school_director",
            "teacher",
            "guardian",
        },
        "retrieve": {
            "national_admin",
            "provincial_admin",
            "district_admin",
            "school_director",
            "teacher",
            "guardian",
        },
    }


class StudentGuardianViewSet(RobustModelViewSet):
    queryset = StudentGuardian.objects.select_related("student", "guardian").all()
    serializer_class = StudentGuardianSerializer
    search_fields = ("student__name", "guardian__name")
    ordering_fields = ("id", "student__name", "guardian__name", "primary_contact")
    ordering = ("student__name", "guardian__name")
    allowed_roles = {
        "*": {
            "national_admin",
            "provincial_admin",
            "district_admin",
            "school_director",
        },
        "list": {
            "national_admin",
            "provincial_admin",
            "district_admin",
            "school_director",
            "teacher",
            "guardian",
        },
        "retrieve": {
            "national_admin",
            "provincial_admin",
            "district_admin",
            "school_director",
            "teacher",
            "guardian",
        },
    }


class StudentOutcomeViewSet(RobustModelViewSet):
    queryset = StudentOutcome.objects.select_related("student", "outcome").all()
    serializer_class = StudentOutcomeSerializer
    search_fields = ("student__name", "outcome__code", "outcome__description", "tenant_id")
    ordering_fields = ("id", "updated_at", "mastery_level", "evidence_count")
    ordering = ("-updated_at",)
    allowed_roles = {
        "*": {
            "national_admin",
            "provincial_admin",
            "district_admin",
            "school_director",
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
