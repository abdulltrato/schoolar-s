from django.db import models

from core.models import BaseCodeModel


class Invoice(BaseCodeModel):
    CODE_PREFIX = "INV"
    STATUS_CHOICES = [
        ("draft", "Rascunho"),
        ("issued", "Emitida"),
        ("paid", "Paga"),
        ("overdue", "Em atraso"),
        ("cancelled", "Cancelada"),
    ]

    student = models.ForeignKey("academic.Student", on_delete=models.CASCADE, verbose_name="Aluno")
    school = models.ForeignKey("school.School", on_delete=models.CASCADE, verbose_name="Escola")
    reference = models.CharField(max_length=50, verbose_name="Referência")
    description = models.TextField(blank=True, verbose_name="Descrição")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    due_date = models.DateField(verbose_name="Data de vencimento")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft", verbose_name="Estado")

    class Meta:
        verbose_name = "Fatura"
        verbose_name_plural = "Faturas"
        constraints = [
            models.UniqueConstraint(
                fields=["reference", "student"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_invoice_reference_student",
            ),
        ]


class Payment(BaseCodeModel):
    CODE_PREFIX = "PAY"
    METHOD_CHOICES = [
        ("cash", "Numerário"),
        ("bank_transfer", "Transferência bancária"),
        ("mobile_money", "Carteira móvel"),
        ("card", "Cartão"),
    ]

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, verbose_name="Fatura")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    payment_date = models.DateField(verbose_name="Data do pagamento")
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default="cash", verbose_name="Método")
    reference = models.CharField(max_length=50, blank=True, verbose_name="Referência")

    class Meta:
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"
