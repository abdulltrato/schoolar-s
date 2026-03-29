from rest_framework import filters

from core.viewsets import RobustModelViewSet
from .models import AcademicYear, Grade, GradeSubject
from .serializers import AcademicYearSerializer, GradeSerializer, GradeSubjectSerializer


class AcademicYearViewSet(RobustModelViewSet):
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["code", "start_date", "end_date"]


class GradeViewSet(RobustModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["number", "name"]


class GradeSubjectViewSet(RobustModelViewSet):
    queryset = GradeSubject.objects.select_related("academic_year", "grade", "subject")
    serializer_class = GradeSubjectSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["subject__name", "grade__number", "academic_year__code"]
