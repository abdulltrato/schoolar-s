from django.db import models

from core.models import BaseCodeModel


class PaymentPlan(BaseCodeModel):
    CODE_PREFIX = "PPN"
    TYPE_CHOICES = [
        ("enrollment_fee", "Taxa de matrícula"),
        ("tuition_monthly", "Mensalidade"),
        ("propina", "Propina"),
        ("exam_regular", "Exame"),
        ("exam_recurrence", "Exame de recorrência"),
        ("exam_special", "Exame especial"),
    ]
    STATUS_CHOICES = [
        ("scheduled", "Agendado"),
        ("invoiced", "Faturado"),
        ("paid", "Pago"),
        ("cancelled", "Cancelado"),
    ]

    enrollment = models.ForeignKey("school.Enrollment", on_delete=models.CASCADE, related_name="payment_plans")
    student = models.ForeignKey("academic.Student", on_delete=models.CASCADE, verbose_name="Aluno")
    school = models.ForeignKey("school.School", on_delete=models.CASCADE, verbose_name="Escola")
    invoice = models.ForeignKey("school.Invoice", null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Fatura")
    type = models.CharField(max_length=30, choices=TYPE_CHOICES, verbose_name="Tipo")
    description = models.CharField(max_length=180, blank=True, verbose_name="Descrição")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    due_date = models.DateField(null=True, blank=True, verbose_name="Data de vencimento")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="scheduled", verbose_name="Estado")

    def __str__(self):
        return f"{self.get_type_display()} - {self.amount} - {self.due_date or ''}"

    class Meta:
        verbose_name = "Plano de pagamento"
        verbose_name_plural = "Planos de pagamento"
        ordering = ["due_date", "type"]
