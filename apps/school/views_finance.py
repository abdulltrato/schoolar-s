from core.viewsets import RobustModelViewSet
# ViewSet base com tratamento robusto de erros.
from .models import Invoice, Payment
# Modelos financeiros.
from .serializers_finance import InvoiceSerializer, PaymentSerializer
# Serializers de faturas e pagamentos.


class InvoiceViewSet(RobustModelViewSet):
    """CRUD de faturas com filtros por status, aluno e escola."""
    queryset = Invoice.objects.select_related("student", "school")
    serializer_class = InvoiceSerializer
    filterset_fields = ["status", "student", "school"]
    search_fields = ["reference", "description", "student__name"]


class PaymentViewSet(RobustModelViewSet):
    """CRUD de pagamentos com filtros por tipo, método e fatura."""
    queryset = Payment.objects.select_related("invoice")
    serializer_class = PaymentSerializer
    filterset_fields = ["payment_type", "method", "invoice"]
    search_fields = ["reference", "invoice__reference", "notes"]
