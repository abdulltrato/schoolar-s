from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseCodeModel

from .enrollment import Enrollment


class AttendanceRecord(BaseCodeModel):
    CODE_PREFIX = "ATT"
    STATUS_CHOICES = [
        ("present", "Presente"),
        ("late", "Atrasado"),
        ("absent", "Falta"),
        ("justified_absence", "Falta justificada"),
    ]

    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, verbose_name="Matrícula")
    lesson_date = models.DateField(verbose_name="Data da aula")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="Estado")
    notes = models.CharField(max_length=255, blank=True, verbose_name="Observações")

    def clean(self):
        enrollment_tenant = (self.enrollment.tenant_id or "").strip() if self.enrollment_id else ""
        if self.tenant_id and enrollment_tenant and self.tenant_id != enrollment_tenant:
            raise ValidationError({"tenant_id": "O tenant de presenças deve coincidir com o tenant da matrícula."})
        if enrollment_tenant and not self.tenant_id:
            self.tenant_id = enrollment_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id é obrigatório."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.enrollment.student} - {self.lesson_date} - {self.status}"

    class Meta:
        unique_together = ("enrollment", "lesson_date")
        verbose_name = "Presença"
        verbose_name_plural = "Presenças"
        ordering = ["-lesson_date"]
