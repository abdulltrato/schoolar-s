from django.core.exceptions import ValidationError
# Exceção de validação.
from django.db import models
# Componentes do ORM.

from core.models import BaseCodeModel
# Modelo base com código e auditoria.

from .enrollment import Enrollment
# Matrícula associada ao registro de presença.


class AttendanceRecord(BaseCodeModel):
    """Registro de assiduidade de um aluno em uma data específica."""

    CODE_PREFIX = "ATT"
    STATUS_CHOICES = [
        ("present", "Presente"),
        ("late", "Atrasado"),
        ("absent", "Falta"),
        ("justified_absence", "Falta justificada"),
    ]

    # Matrícula do aluno.
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, verbose_name="Matrícula")
    # Data da aula.
    lesson_date = models.DateField(verbose_name="Data da aula")
    # Estado de presença.
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="Estado")
    # Observações opcionais.
    notes = models.CharField(max_length=255, blank=True, verbose_name="Observações")

    def clean(self):
        """Valida alinhamento de tenant com a matrícula."""
        enrollment_tenant = (self.enrollment.tenant_id or "").strip() if self.enrollment_id else ""
        if self.tenant_id and enrollment_tenant and self.tenant_id != enrollment_tenant:
            raise ValidationError({"tenant_id": "O tenant de presenças deve coincidir com o tenant da matrícula."})
        if enrollment_tenant and not self.tenant_id:
            self.tenant_id = enrollment_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id é obrigatório."})

    def save(self, *args, **kwargs):
        """Valida e persiste o registro."""
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        """Exibe aluno, data e status."""
        return f"{self.enrollment.student} - {self.lesson_date} - {self.status}"

    class Meta:
        # Uma presença por matrícula por data.
        unique_together = ("enrollment", "lesson_date")
        verbose_name = "Presença"
        verbose_name_plural = "Presenças"
        ordering = ["-lesson_date"]
