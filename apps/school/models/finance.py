from django.core.exceptions import ValidationError
# Exceção de validação.
from django.db import models
# Campos do ORM.

from core.models import BaseCodeModel
# Modelo base com código e auditoria.

from .school import School
# Escola associada às faturas.


class Invoice(BaseCodeModel):
    """Fatura emitida para um aluno, vinculada a uma escola e valores devidos."""

    CODE_PREFIX = "INV"
    STATUS_CHOICES = [
        ("draft", "Rascunho"),
        ("issued", "Emitida"),
        ("paid", "Paga"),
        ("overdue", "Em atraso"),
        ("cancelled", "Cancelada"),
    ]

    # Aluno devedor.
    student = models.ForeignKey("academic.Student", on_delete=models.CASCADE, verbose_name="Aluno")
    # Escola emissora.
    school = models.ForeignKey(School, on_delete=models.CASCADE, verbose_name="Escola")
    # Referência única para pagamentos/controle.
    reference = models.CharField(max_length=40, unique=True, verbose_name="Referência")
    # Descrição da cobrança.
    description = models.CharField(max_length=180, verbose_name="Descrição")
    # Valor total.
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    # Vencimento.
    due_date = models.DateField(verbose_name="Vencimento")
    # Estado atual da fatura.
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft", verbose_name="Estado")
    # Data de emissão.
    issued_at = models.DateTimeField(auto_now_add=True, verbose_name="Emitida em")

    def clean(self):
        """Alinha tenant entre aluno e escola e preenche tenant_id."""
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
        """Valida e salva fatura."""
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        """Representa pela referência."""
        return self.reference

    class Meta:
        # Rótulos e ordenação por emissão mais recente.
        verbose_name = "Fatura"
        verbose_name_plural = "Faturas"
        ordering = ["-issued_at"]


class Payment(BaseCodeModel):
    """Pagamento associado a uma fatura, com método e tipo."""

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

    # Fatura paga.
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="payments", verbose_name="Fatura")
    # Valor do pagamento.
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor pago")
    # Data do pagamento.
    payment_date = models.DateField(verbose_name="Data do pagamento")
    # Meio utilizado.
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, verbose_name="Método")
    # Tipo da cobrança liquidada.
    payment_type = models.CharField(
        max_length=30, choices=PAYMENT_TYPE_CHOICES, default="other", verbose_name="Tipo de pagamento"
    )
    # Referência externa opcional.
    reference = models.CharField(max_length=60, blank=True, verbose_name="Referência")
    # Observações livres.
    notes = models.CharField(max_length=255, blank=True, verbose_name="Observações")

    def clean(self):
        """Herda tenant da fatura e valida consistência."""
        invoice_tenant = (self.invoice.tenant_id or "").strip() if self.invoice_id else ""
        if self.tenant_id and invoice_tenant and self.tenant_id != invoice_tenant:
            raise ValidationError({"tenant_id": "O tenant do pagamento deve coincidir com o tenant da fatura."})
        if invoice_tenant and not self.tenant_id:
            self.tenant_id = invoice_tenant

    def save(self, *args, **kwargs):
        """Valida antes de persistir."""
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        """Mostra referência da fatura e valor pago."""
        return f"{self.invoice.reference} - {self.amount}"

    class Meta:
        # Ordena pagamentos mais recentes primeiro.
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"
        ordering = ["-payment_date"]
