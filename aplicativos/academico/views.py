from .models import Aluno
from .serializers import AlunoSerializer
from nucleo.viewsets import RobustModelViewSet

class AlunoViewSet(RobustModelViewSet):
    queryset = Aluno.objects.prefetch_related("alunocompetencia_set__competencia").all()
    serializer_class = AlunoSerializer
    search_fields = ("nome", "estado")
    ordering_fields = ("id", "nome", "classe", "ciclo", "data_nascimento")
    ordering = ("nome",)
