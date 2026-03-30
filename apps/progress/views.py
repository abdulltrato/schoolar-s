from rest_framework import status
# Códigos HTTP.
from rest_framework.decorators import action
# Decorador para actions customizadas.
from rest_framework.response import Response
# Respostas DRF.

from core.viewsets import RobustModelViewSet
# ViewSet base com tratamento robusto.
from .evaluation import EvaluationError, evaluate_student_progress
# Motor de avaliação de progresso.

from .models import Progression
# Modelo de progressão.
from .serializers import ProgressionSerializer
# Serializer correspondente.


class ProgressionViewSet(RobustModelViewSet):
    """CRUD de progressões e utilitário para avaliar situação do aluno."""
    queryset = Progression.objects.select_related("student").all()
    serializer_class = ProgressionSerializer
    search_fields = ("student__name", "academic_year", "decision")
    ordering_fields = ("id", "decision_date", "academic_year", "decision")
    ordering = ("-decision_date",)

    @action(methods=["post"], detail=False, url_path="avaliar")
    def avaliar_progressao(self, request):
        """
        Endpoint utilitário para calcular a situação do aluno antes de registrar uma progressão.
        """
        data = request.data or {}
        try:
            resultado = evaluate_student_progress(
                teste1=data.get("teste1"),
                teste2=data.get("teste2"),
                teste3=data.get("teste3"),
                exame=data.get("exame"),
                exame_recorrencia=data.get("exame_recorrencia"),
                exame_especial=data.get("exame_especial"),
            )
        except EvaluationError as exc:
            return Response({"erro": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(resultado, status=status.HTTP_200_OK)
