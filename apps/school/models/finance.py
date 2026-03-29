from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseCodeModel

from .school import School


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
    school = models.ForeignKey(School, on_delete=models.CASCADE, verbose_name="Escola")
    reference = models.CharField(max_length=40, unique=True, verbose_name="Referência")
    description = models.CharField(max_length=180, verbose_name="Descrição")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    due_date = models.DateField(verbose_name="Vencimento")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft", verbose_name="Estado")
    issued_at = models.DateTimeField(auto_now_add=True, verbose_name="Emitida em")

    def clean(self):
        student_tenant = (self.student.tenant_id or "").strip() if self.student_id else ""
        school_tenant = (self.school.tenant_id or "").strip() if self.school_id else ""
        if self.tenant_id and student_tenant and self.tenant_id != student_tenant:
            raise ValidationError({"tenant_id": "O tenant da fatura deve coincidir com o tenant do aluno."})
        if self.tenant_id and school_tenant and self.tenant_id != school_tenant:
            raise ValidationError({"tenant_id": "O tenant da fatura deve coincidir com o tenant da escola."})
        if student_tenant and school_tenant and student_tenant != school_tenant:
            raise ValidationError({"tenant_id": "Aluno e escola devem pertencer ao mesmo tenant."})
        self.tenant_id = self.tenant_id or student_tenant or school_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id é obrigatório."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.reference

    class Meta:
        verbose_name = "Fatura"
        verbose_name_plural = "Faturas"
        ordering = ["-issued_at"]


class Payment(BaseCodeModel):
    CODE_PREFIX = "PGT"
    METHOD_CHOICES = [
        ("cash", "Numerário"),
        ("bank_transfer", "Transferência"),
        ("mobile_money", "Carteira móvel"),
        ("card", "Cartão"),
    ]
    PAYMENT_TYPE_CHOICES = [
        ("enrollment_fee", "Taxa de matrícula"),
        ("tuition_monthly", "Mensalidade"),
        ("propina", "Propina"),
        ("exam_regular", "Exame"),
        ("exam_recurrence", "Exame de recorrência"),
        ("exam_special", "Exame especial"),
        ("other", "Outro"),
    ]

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="payments", verbose_name="Fatura")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor pago")
    payment_date = models.DateField(verbose_name="Data do pagamento")
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, verbose_name="Método")
    payment_type = models.CharField(
        max_length=30, choices=PAYMENT_TYPE_CHOICES, default="other", verbose_name="Tipo de pagamento"
    )
    reference = models.CharField(max_length=60, blank=True, verbose_name="Referência")
    notes = models.CharField(max_length=255, blank=True, verbose_name="Observações")

    def clean(self):
        invoice_tenant = (self.invoice.tenant_id or "").strip() if self.invoice_id else ""
        if self.tenant_id and invoice_tenant and self.tenant_id != invoice_tenant:
            raise ValidationError({"tenant_id": "O tenant do pagamento deve coincidir com o tenant da fatura."})
        if invoice_tenant and not self.tenant_id:
            self.tenant_id = invoice_tenant

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice.reference} - {self.amount}"

    class Meta:
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"
        ordering = ["-payment_date"]
