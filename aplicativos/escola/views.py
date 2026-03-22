from .models import AlocacaoDocente, AnoLetivo, AtribuicaoGestao, Classe, DisciplinaClasse, Escola, Matricula, Professor, Turma
from .serializers import (
    AlocacaoDocenteSerializer,
    AnoLetivoSerializer,
    AtribuicaoGestaoSerializer,
    ClasseSerializer,
    DisciplinaClasseSerializer,
    EscolaSerializer,
    MatriculaSerializer,
    ProfessorSerializer,
    TurmaSerializer,
)
from nucleo.viewsets import RobustModelViewSet


class AnoLetivoViewSet(RobustModelViewSet):
    queryset = AnoLetivo.objects.all()
    serializer_class = AnoLetivoSerializer
    search_fields = ("codigo",)
    ordering_fields = ("id", "codigo", "data_inicio", "data_fim", "ativo")
    ordering = ("-codigo",)


class ClasseViewSet(RobustModelViewSet):
    queryset = Classe.objects.all()
    serializer_class = ClasseSerializer
    search_fields = ("numero", "nome")
    ordering_fields = ("id", "numero", "ciclo", "nome")
    ordering = ("numero",)


class EscolaViewSet(RobustModelViewSet):
    queryset = Escola.objects.all()
    serializer_class = EscolaSerializer
    search_fields = ("codigo", "nome", "distrito", "provincia")
    ordering_fields = ("id", "codigo", "nome", "distrito", "provincia")
    ordering = ("nome",)


class ProfessorViewSet(RobustModelViewSet):
    queryset = Professor.objects.select_related("escola").all()
    serializer_class = ProfessorSerializer
    search_fields = ("nome", "especialidade", "user__username", "escola__nome")
    ordering_fields = ("id", "nome", "especialidade", "escola__nome")
    ordering = ("nome",)


class TurmaViewSet(RobustModelViewSet):
    queryset = Turma.objects.select_related("escola", "classe", "ano_letivo", "professor_responsavel").all()
    serializer_class = TurmaSerializer
    search_fields = ("nome", "ano_letivo__codigo", "classe__nome", "professor_responsavel__nome", "escola__nome")
    ordering_fields = ("id", "nome", "ciclo", "ano_letivo__codigo", "classe__numero", "escola__nome")
    ordering = ("ano_letivo__codigo", "classe__numero", "nome")


class DisciplinaClasseViewSet(RobustModelViewSet):
    queryset = DisciplinaClasse.objects.select_related("ano_letivo", "classe", "disciplina").all()
    serializer_class = DisciplinaClasseSerializer
    search_fields = ("ano_letivo__codigo", "classe__nome", "disciplina__nome")
    ordering_fields = ("id", "ano_letivo__codigo", "classe__numero", "disciplina__nome")
    ordering = ("ano_letivo__codigo", "classe__numero", "disciplina__nome")


class AlocacaoDocenteViewSet(RobustModelViewSet):
    queryset = AlocacaoDocente.objects.select_related(
        "professor",
        "professor__escola",
        "turma",
        "turma__escola",
        "turma__ano_letivo",
        "turma__classe",
        "disciplina_classe",
        "disciplina_classe__disciplina",
    ).all()
    serializer_class = AlocacaoDocenteSerializer
    search_fields = ("professor__nome", "turma__nome", "disciplina_classe__disciplina__nome", "turma__escola__nome")
    ordering_fields = ("id", "professor__nome", "turma__nome", "disciplina_classe__disciplina__nome")
    ordering = ("turma__ano_letivo__codigo", "turma__classe__numero", "turma__nome")


class MatriculaViewSet(RobustModelViewSet):
    queryset = Matricula.objects.select_related("aluno", "turma", "turma__escola", "turma__ano_letivo", "turma__classe").all()
    serializer_class = MatriculaSerializer
    search_fields = ("aluno__nome", "turma__nome", "turma__ano_letivo__codigo", "turma__escola__nome")
    ordering_fields = ("id", "data_matricula", "aluno__nome", "turma__nome")
    ordering = ("-data_matricula",)


class AtribuicaoGestaoViewSet(RobustModelViewSet):
    queryset = AtribuicaoGestao.objects.select_related(
        "professor",
        "professor__escola",
        "escola",
        "ano_letivo",
        "classe",
        "turma",
    ).all()
    serializer_class = AtribuicaoGestaoSerializer
    search_fields = ("professor__nome", "escola__nome", "cargo", "ano_letivo__codigo")
    ordering_fields = ("id", "professor__nome", "escola__nome", "cargo", "ano_letivo__codigo")
    ordering = ("ano_letivo__codigo", "escola__nome", "cargo")
