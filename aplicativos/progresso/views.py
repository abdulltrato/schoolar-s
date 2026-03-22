from .models import Progressao
from .serializers import ProgressaoSerializer
from nucleo.viewsets import RobustModelViewSet

class ProgressaoViewSet(RobustModelViewSet):
    queryset = Progressao.objects.select_related("aluno").all()
    serializer_class = ProgressaoSerializer
    search_fields = ("aluno__nome", "ano_letivo", "decisao")
    ordering_fields = ("id", "data_decisao", "ano_letivo", "decisao")
    ordering = ("-data_decisao",)
