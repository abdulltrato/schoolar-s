from rest_framework import filters

from core.viewsets import RobustModelViewSet
from .models import Classroom, School, Teacher, TeachingAssignment
from .serializers import ClassroomSerializer, SchoolSerializer, TeacherSerializer, TeachingAssignmentSerializer


class SchoolViewSet(RobustModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "district", "province"]


class TeacherViewSet(RobustModelViewSet):
    queryset = Teacher.objects.select_related("school", "specialty").order_by("name")
    serializer_class = TeacherSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "school__name", "specialty__name"]


class ClassroomViewSet(RobustModelViewSet):
    queryset = Classroom.objects.select_related("grade", "academic_year", "school", "lead_teacher")
    serializer_class = ClassroomSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "academic_year__code", "grade__number"]


class TeachingAssignmentViewSet(RobustModelViewSet):
    queryset = TeachingAssignment.objects.select_related("teacher", "classroom", "grade_subject")
    serializer_class = TeachingAssignmentSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["teacher__name", "classroom__name", "grade_subject__subject__name"]
