from .models import AreaCurricular, Competencia, CurriculoBase, CurriculoLocal, Disciplina, PlanoCurricularDisciplina
from .serializers import (
    AreaCurricularSerializer,
    CompetenciaSerializer,
    CurriculoBaseSerializer,
    CurriculoLocalSerializer,
    DisciplinaSerializer,
    PlanoCurricularDisciplinaSerializer,
)
from nucleo.viewsets import RobustModelViewSet


class AreaCurricularViewSet(RobustModelViewSet):
    queryset = AreaCurricular.objects.all()
    serializer_class = AreaCurricularSerializer
    search_fields = ("nome",)
    ordering_fields = ("id", "nome")
    ordering = ("nome",)


class DisciplinaViewSet(RobustModelViewSet):
    queryset = Disciplina.objects.select_related("area").all()
    serializer_class = DisciplinaSerializer
    search_fields = ("nome", "area__nome")
    ordering_fields = ("id", "nome", "ciclo", "area__nome")
    ordering = ("nome",)


class CompetenciaViewSet(RobustModelViewSet):
    queryset = Competencia.objects.select_related("disciplina", "disciplina__area").all()
    serializer_class = CompetenciaSerializer
    search_fields = ("nome", "area", "disciplina__nome")
    ordering_fields = ("id", "nome", "ciclo", "area")
    ordering = ("nome",)


class CurriculoBaseViewSet(RobustModelViewSet):
    queryset = CurriculoBase.objects.prefetch_related("competencias").all()
    serializer_class = CurriculoBaseSerializer
    ordering_fields = ("id", "ciclo")
    ordering = ("ciclo",)


class CurriculoLocalViewSet(RobustModelViewSet):
    queryset = CurriculoLocal.objects.prefetch_related("competencias_adicionais").all()
    serializer_class = CurriculoLocalSerializer
    search_fields = ("tenant_id",)
    ordering_fields = ("id", "tenant_id", "ciclo")
    ordering = ("tenant_id", "ciclo")


class PlanoCurricularDisciplinaViewSet(RobustModelViewSet):
    queryset = PlanoCurricularDisciplina.objects.select_related(
        "disciplina_classe",
        "disciplina_classe__ano_letivo",
        "disciplina_classe__classe",
        "disciplina_classe__disciplina",
    ).prefetch_related("competencias_previstas").all()
    serializer_class = PlanoCurricularDisciplinaSerializer
    search_fields = (
        "disciplina_classe__ano_letivo__codigo",
        "disciplina_classe__classe__nome",
        "disciplina_classe__disciplina__nome",
    )
    ordering_fields = (
        "id",
        "disciplina_classe__ano_letivo__codigo",
        "disciplina_classe__classe__numero",
        "disciplina_classe__disciplina__nome",
    )
    ordering = ("disciplina_classe__ano_letivo__codigo", "disciplina_classe__classe__numero")
