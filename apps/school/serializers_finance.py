from rest_framework import serializers

from .models import Invoice, Payment


class InvoiceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.name", read_only=True)
    school_name = serializers.CharField(source="school.name", read_only=True)

    class Meta:
        model = Invoice
        fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):
    invoice_reference = serializers.CharField(source="invoice.reference", read_only=True)

    class Meta:
        model = Payment
        fields = "__all__"
