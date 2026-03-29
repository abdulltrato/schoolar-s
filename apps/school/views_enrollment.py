from rest_framework import filters

from core.viewsets import RobustModelViewSet
from .models import AttendanceRecord, Enrollment
from .serializers import AttendanceRecordSerializer, EnrollmentSerializer, EnrollmentSummarySerializer


class EnrollmentViewSet(RobustModelViewSet):
    queryset = Enrollment.objects.select_related("student", "classroom")
    serializer_class = EnrollmentSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["student__name", "classroom__name", "classroom__academic_year__code"]


class EnrollmentSummaryViewSet(RobustModelViewSet):
    queryset = Enrollment.objects.select_related("student", "classroom")
    serializer_class = EnrollmentSummarySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["student__name", "classroom__name", "classroom__academic_year__code"]


class AttendanceRecordViewSet(RobustModelViewSet):
    queryset = AttendanceRecord.objects.select_related("enrollment__student", "enrollment__classroom")
    serializer_class = AttendanceRecordSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["enrollment__student__name", "enrollment__classroom__name"]
