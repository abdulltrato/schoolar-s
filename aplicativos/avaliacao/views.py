from .models import Avaliacao, ComponenteAvaliativa, PeriodoAvaliativo, ResultadoPeriodoDisciplina
from .serializers import (
    AvaliacaoSerializer,
    ComponenteAvaliativaSerializer,
    PeriodoAvaliativoSerializer,
    ResultadoPeriodoDisciplinaSerializer,
)
from nucleo.viewsets import RobustModelViewSet


class PeriodoAvaliativoViewSet(RobustModelViewSet):
    queryset = PeriodoAvaliativo.objects.select_related("ano_letivo").all()
    serializer_class = PeriodoAvaliativoSerializer
    search_fields = ("nome", "ano_letivo__codigo")
    ordering_fields = ("id", "ano_letivo__codigo", "ordem", "nome")
    ordering = ("ano_letivo__codigo", "ordem")


class ComponenteAvaliativaViewSet(RobustModelViewSet):
    queryset = ComponenteAvaliativa.objects.select_related(
        "periodo",
        "periodo__ano_letivo",
        "disciplina_classe",
        "disciplina_classe__classe",
        "disciplina_classe__disciplina",
    ).all()
    serializer_class = ComponenteAvaliativaSerializer
    search_fields = ("nome", "tipo", "periodo__nome", "disciplina_classe__disciplina__nome")
    ordering_fields = ("id", "periodo__ordem", "disciplina_classe__disciplina__nome", "nome", "peso")
    ordering = ("periodo__ano_letivo__codigo", "periodo__ordem", "disciplina_classe__disciplina__nome")


class AvaliacaoViewSet(RobustModelViewSet):
    queryset = Avaliacao.objects.select_related(
        "aluno",
        "competencia",
        "periodo",
        "componente",
        "alocacao_docente",
        "alocacao_docente__professor",
        "alocacao_docente__turma",
        "alocacao_docente__turma__ano_letivo",
        "alocacao_docente__turma__classe",
        "alocacao_docente__disciplina_classe",
        "alocacao_docente__disciplina_classe__disciplina",
    ).all()
    serializer_class = AvaliacaoSerializer
    search_fields = (
        "aluno__nome",
        "competencia__nome",
        "tipo",
        "periodo__nome",
        "componente__nome",
        "alocacao_docente__disciplina_classe__disciplina__nome",
        "alocacao_docente__turma__nome",
    )
    ordering_fields = ("id", "data", "tipo", "aluno__nome", "alocacao_docente__turma__nome", "periodo__ordem")
    ordering = ("-data",)


class ResultadoPeriodoDisciplinaViewSet(RobustModelViewSet):
    queryset = ResultadoPeriodoDisciplina.objects.select_related(
        "aluno",
        "periodo",
        "periodo__ano_letivo",
        "alocacao_docente",
        "alocacao_docente__professor",
        "alocacao_docente__turma",
        "alocacao_docente__disciplina_classe",
        "alocacao_docente__disciplina_classe__disciplina",
    ).all()
    serializer_class = ResultadoPeriodoDisciplinaSerializer
    search_fields = ("aluno__nome", "periodo__nome", "alocacao_docente__disciplina_classe__disciplina__nome")
    ordering_fields = ("id", "media_final", "periodo__ordem", "aluno__nome")
    ordering = ("periodo__ano_letivo__codigo", "periodo__ordem", "aluno__nome")
