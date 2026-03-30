from rest_framework import filters
# Filtros de busca do DRF.

from core.viewsets import RobustModelViewSet
# ViewSet base com tratamento robusto.
from .models import Classroom, School, Teacher, TeachingAssignment
# Modelos escolares.
from .serializers import ClassroomSerializer, SchoolSerializer, TeacherSerializer, TeachingAssignmentSerializer
# Serializers correspondentes.


class SchoolViewSet(RobustModelViewSet):
    """CRUD de escolas/tenants com busca por nome e localização."""
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "district", "province"]


class TeacherViewSet(RobustModelViewSet):
    """CRUD de professores, incluindo escola e especialidade carregadas."""
    queryset = Teacher.objects.select_related("school", "specialty").order_by("name")
    serializer_class = TeacherSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "school__name", "specialty__name"]


class ClassroomViewSet(RobustModelViewSet):
    """CRUD de turmas com relações pré-carregadas para evitar N+1."""
    queryset = Classroom.objects.select_related("grade", "academic_year", "school", "lead_teacher")
    serializer_class = ClassroomSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "academic_year__code", "grade__number"]


class TeachingAssignmentViewSet(RobustModelViewSet):
    """CRUD de alocações docentes."""
    queryset = TeachingAssignment.objects.select_related("teacher", "classroom", "grade_subject")
    serializer_class = TeachingAssignmentSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["teacher__name", "classroom__name", "grade_subject__subject__name"]
