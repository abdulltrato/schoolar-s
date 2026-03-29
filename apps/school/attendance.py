from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseCodeModel


class AttendanceRecord(BaseCodeModel):
    CODE_PREFIX = "ATR"

    STATUS_CHOICES = [
        ("present", "Presente"),
        ("late", "Atraso"),
        ("absent", "Falta"),
        ("justified_absence", "Falta justificada"),
    ]

    enrollment = models.ForeignKey("school.Enrollment", on_delete=models.CASCADE, verbose_name="Matrícula")
    lesson_date = models.DateField(verbose_name="Data da aula")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, verbose_name="Estado")
    notes = models.TextField(blank=True, verbose_name="Notas")

    class Meta:
        verbose_name = "Registro de presença"
        verbose_name_plural = "Registros de presença"
        constraints = [
            models.UniqueConstraint(
                fields=["enrollment", "lesson_date"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_attendance_record_active",
            ),
        ]

    def clean(self):
        if self.lesson_date is None:
            raise ValidationError({"lesson_date": "Informe a data."})
