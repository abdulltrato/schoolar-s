import re

from django.core.exceptions import ValidationError
from django.db import models


class Progression(models.Model):
    DECISION_CHOICES = [
        ("approved", "Aprovado"),
        ("retained", "Retido"),
        ("transferred", "Transferido"),
    ]

    student = models.ForeignKey("academic.Student", on_delete=models.CASCADE, verbose_name="Aluno")
    tenant_id = models.CharField(max_length=50, blank=True, verbose_name="Identificador do tenant")
    cycle = models.IntegerField(verbose_name="Ciclo")
    academic_year = models.CharField(max_length=10, verbose_name="Ano letivo")
    decision_date = models.DateField(verbose_name="Data da decisão")
    decision = models.CharField(max_length=20, choices=DECISION_CHOICES, verbose_name="Decisão")
    comment = models.TextField(blank=True, verbose_name="Comentário")

    def clean(self):
        student_tenant = (self.student.tenant_id or "").strip() if self.student_id else ""
        if student_tenant:
            if self.tenant_id and self.tenant_id != student_tenant:
                raise ValidationError({"tenant_id": "Progression tenant must match the student tenant."})
            if not self.tenant_id:
                self.tenant_id = student_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id is required."})
        if self.cycle not in {1, 2}:
            raise ValidationError({"cycle": "The progression cycle must be 1 or 2."})
        if self.student_id and self.student.cycle != self.cycle:
            raise ValidationError({"cycle": "The progression cycle must match the student cycle."})
        if not re.fullmatch(r"\d{4}-\d{4}", self.academic_year):
            raise ValidationError({"academic_year": "Use the YYYY-YYYY format."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Progression {self.student} cycle {self.cycle} - {self.decision}"

    class Meta:
        verbose_name = "Progressão"
        verbose_name_plural = "Progressões"
        ordering = ["-decision_date"]
