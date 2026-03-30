from rest_framework import serializers
# Base de serializers do DRF.

from .models import Invoice, Payment
# Modelos financeiros.


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializa faturas com nomes de aluno/escola e ano letivo derivado."""

    student_name = serializers.CharField(source="student.name", read_only=True)
    school_name = serializers.CharField(source="school.name", read_only=True)
    academic_year = serializers.CharField(source="student.academic_year", read_only=True)

    class Meta:
        model = Invoice
        fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):
    """Serializa pagamentos incluindo referência da fatura e label do tipo."""

    invoice_reference = serializers.CharField(source="invoice.reference", read_only=True)
    payment_type_label = serializers.CharField(source="get_payment_type_display", read_only=True)

    class Meta:
        model = Payment
        fields = "__all__"
