from rest_framework import serializers

from .models import Invoice, Payment


class InvoiceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.name", read_only=True)
    school_name = serializers.CharField(source="school.name", read_only=True)
    academic_year = serializers.CharField(source="student.academic_year", read_only=True)

    class Meta:
        model = Invoice
        fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):
    invoice_reference = serializers.CharField(source="invoice.reference", read_only=True)
    payment_type_label = serializers.CharField(source="get_payment_type_display", read_only=True)

    class Meta:
        model = Payment
        fields = "__all__"
