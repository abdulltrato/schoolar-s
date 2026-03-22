from .models import Professor, Turma, Matricula
from .serializers import ProfessorSerializer, TurmaSerializer, MatriculaSerializer
from nucleo.viewsets import RobustModelViewSet


class ProfessorViewSet(RobustModelViewSet):
    queryset = Professor.objects.all()
    serializer_class = ProfessorSerializer
    search_fields = ("nome", "especialidade", "user__username")
    ordering_fields = ("id", "nome", "especialidade")
    ordering = ("nome",)


class TurmaViewSet(RobustModelViewSet):
    queryset = Turma.objects.select_related("professor_responsavel").all()
    serializer_class = TurmaSerializer
    search_fields = ("nome", "ano_letivo", "professor_responsavel__nome")
    ordering_fields = ("id", "nome", "ciclo", "ano_letivo")
    ordering = ("nome",)


class MatriculaViewSet(RobustModelViewSet):
    queryset = Matricula.objects.select_related("aluno", "turma").all()
    serializer_class = MatriculaSerializer
    search_fields = ("aluno__nome", "turma__nome")
    ordering_fields = ("id", "data_matricula", "aluno__nome", "turma__nome")
    ordering = ("-data_matricula",)
