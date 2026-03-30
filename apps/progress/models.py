import re
# Regex para validar formato do ano letivo.

from django.core.exceptions import ValidationError
# Exceção de validação.
from django.db import models
# Campos do ORM.

from core.models import BaseCodeModel
# Modelo base com código e auditoria.


class Progression(BaseCodeModel):
    """Decisão de progressão/retenção/transferência de um aluno em um ciclo e ano letivo."""

    CODE_PREFIX = "PRG"
    DECISION_CHOICES = [
        ("approved", "Aprovado"),
        ("retained", "Retido"),
        ("transferred", "Transferido"),
    ]

    # Aluno avaliado.
    student = models.ForeignKey("academic.Student", on_delete=models.CASCADE, verbose_name="Aluno")
    # Ciclo de ensino (1 ou 2).
    cycle = models.IntegerField(verbose_name="Ciclo")
    # Ano letivo no formato YYYY-YYYY.
    academic_year = models.CharField(max_length=10, verbose_name="Ano letivo")
    # Data em que a decisão foi tomada.
    decision_date = models.DateField(verbose_name="Data da decisão")
    # Decisão final.
    decision = models.CharField(max_length=20, choices=DECISION_CHOICES, verbose_name="Decisão")
    # Comentário opcional.
    comment = models.TextField(blank=True, verbose_name="Comentário")

    def clean(self):
        """Valida tenant, ciclo e formato do ano letivo, sincronizando dados com o aluno."""
        student_tenant = (self.student.tenant_id or "").strip() if self.student_id else ""
        if student_tenant:
            if self.tenant_id and self.tenant_id != student_tenant:
                raise ValidationError({"tenant_id": "O tenant da progressão deve coincidir com o tenant do aluno."})
            if not self.tenant_id:
                self.tenant_id = student_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id is required."})
        if self.cycle not in {1, 2}:
            raise ValidationError({"cycle": "O ciclo da progressão deve ser 1 ou 2."})
        if self.student_id and self.student.cycle != self.cycle:
            raise ValidationError({"cycle": "O ciclo da progressão deve coincidir com o ciclo do aluno."})
        normalized = (self.academic_year or "").replace("/", "-").strip()
        if not re.fullmatch(r"\d{4}-\d{4}", normalized):
            raise ValidationError({"academic_year": "Use o formato YYYY-YYYY."})
        self.academic_year = normalized

    def save(self, *args, **kwargs):
        """Valida antes de persistir."""
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        """Exibe aluno, ciclo e decisão."""
        return f"Progression {self.student} cycle {self.cycle} - {self.decision}"

    class Meta:
        # Rótulos administrativos e ordenação por data de decisão desc.
        verbose_name = "Progressão"
        verbose_name_plural = "Progressões"
        ordering = ["-decision_date"]
