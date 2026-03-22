from .models import Avaliacao
from .serializers import AvaliacaoSerializer
from nucleo.viewsets import RobustModelViewSet

class AvaliacaoViewSet(RobustModelViewSet):
    queryset = Avaliacao.objects.select_related("aluno", "competencia").all()
    serializer_class = AvaliacaoSerializer
    search_fields = ("aluno__nome", "competencia__nome", "tipo")
    ordering_fields = ("id", "data", "tipo", "aluno__nome")
    ordering = ("-data",)
