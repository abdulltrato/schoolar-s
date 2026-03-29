from core.viewsets import RobustModelViewSet
from .models import Invoice, Payment
from .serializers_finance import InvoiceSerializer, PaymentSerializer


class InvoiceViewSet(RobustModelViewSet):
    queryset = Invoice.objects.select_related("student", "school")
    serializer_class = InvoiceSerializer
    filterset_fields = ["status", "student", "school"]
    search_fields = ["reference", "description", "student__name"]


class PaymentViewSet(RobustModelViewSet):
    queryset = Payment.objects.select_related("invoice")
    serializer_class = PaymentSerializer
    filterset_fields = ["payment_type", "method", "invoice"]
    search_fields = ["reference", "invoice__reference", "notes"]
