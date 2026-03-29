from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseCodeModel

from .classroom import Classroom


class Enrollment(BaseCodeModel):
    CODE_PREFIX = "MAT"

    student = models.ForeignKey("academic.Student", on_delete=models.CASCADE, verbose_name="Aluno")
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, verbose_name="Turma")
    enrollment_date = models.DateField(auto_now_add=True, verbose_name="Data de matrícula")
    enrollment_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Taxa de matrícula")
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Mensalidade")
    monthly_fee_start = models.DateField(null=True, blank=True, verbose_name="Início cobrança mensalidade")
    monthly_fee_end = models.DateField(null=True, blank=True, verbose_name="Fim cobrança mensalidade")
    exam_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Taxa de exame")
    exam_recurrence_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Taxa de exame de recorrência"
    )
    exam_special_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Taxa de exame especial"
    )

    def clean(self):
        if self.student_id and self.classroom_id:
            student_tenant = (self.student.tenant_id or "").strip()
            classroom_tenant = (self.classroom.tenant_id or "").strip()
            if student_tenant and classroom_tenant and student_tenant != classroom_tenant:
                raise ValidationError({"tenant_id": "Aluno e turma devem pertencer ao mesmo tenant."})
            if self.tenant_id and student_tenant and self.tenant_id != student_tenant:
                raise ValidationError({"tenant_id": "O tenant da matrícula deve coincidir com o tenant do aluno."})
            if self.tenant_id and classroom_tenant and self.tenant_id != classroom_tenant:
                raise ValidationError({"tenant_id": "O tenant da matrícula deve coincidir com o tenant da turma."})
            self.tenant_id = self.tenant_id or student_tenant or classroom_tenant
            if self.student.cycle != self.classroom.cycle:
                raise ValidationError("O ciclo da turma deve coincidir com o ciclo do aluno.")
            if self.student.grade != self.classroom.grade.number:
                raise ValidationError("A classe da turma deve coincidir com a classe do aluno.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Enrollment for {self.student} in {self.classroom}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "classroom"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_enrollment_active",
            ),
        ]
        verbose_name = "Matrícula"
        verbose_name_plural = "Matrículas"
        ordering = ["-enrollment_date"]
