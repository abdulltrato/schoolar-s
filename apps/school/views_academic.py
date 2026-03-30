from rest_framework import filters
# Filtros de busca do DRF.

from core.viewsets import RobustModelViewSet
# ViewSet com tratamento robusto de erros.
from .models import AcademicYear, Grade, GradeSubject
# Modelos acadêmicos.
from .serializers import AcademicYearSerializer, GradeSerializer, GradeSubjectSerializer
# Serializers correspondentes.


class AcademicYearViewSet(RobustModelViewSet):
    """CRUD de anos letivos com busca por código e datas."""
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["code", "start_date", "end_date"]


class GradeViewSet(RobustModelViewSet):
    """CRUD de classes/anos escolares."""
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["number", "name"]


class GradeSubjectViewSet(RobustModelViewSet):
    """CRUD de disciplinas ofertadas por classe/ano, com pré-carregamento de relações."""
    queryset = GradeSubject.objects.select_related("academic_year", "grade", "subject")
    serializer_class = GradeSubjectSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["subject__name", "grade__number", "academic_year__code"]
