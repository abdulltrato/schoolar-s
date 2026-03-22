from .models import Relatorio
from .serializers import RelatorioSerializer
from nucleo.viewsets import RobustModelViewSet

class RelatorioViewSet(RobustModelViewSet):
    queryset = Relatorio.objects.select_related("aluno").all()
    serializer_class = RelatorioSerializer
    search_fields = ("titulo", "tipo", "periodo", "aluno__nome")
    ordering_fields = ("id", "titulo", "tipo", "periodo", "data_geracao")
    ordering = ("-data_geracao",)
