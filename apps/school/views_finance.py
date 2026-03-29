from core.viewsets import RobustModelViewSet
from .models import Invoice, Payment
from .serializers import InvoiceSerializer, PaymentSerializer


class InvoiceViewSet(RobustModelViewSet):
    queryset = Invoice.objects.select_related("student", "school")
    serializer_class = InvoiceSerializer


class PaymentViewSet(RobustModelViewSet):
    queryset = Payment.objects.select_related("invoice")
    serializer_class = PaymentSerializer
