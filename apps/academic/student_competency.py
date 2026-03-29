from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseCodeModel
from .student import Student


class StudentCompetency(BaseCodeModel):
    CODE_PREFIX = "STC"

    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="Aluno")
    competency = models.ForeignKey("curriculum.Competency", on_delete=models.CASCADE, verbose_name="Competência")
    nivel = models.DecimalField(max_digits=3, decimal_places=1, default=0.0, verbose_name="Nível")  # e.g., 0.0 to 5.0

    def clean(self):
        student_tenant = (self.student.tenant_id or "").strip() if self.student_id else ""
        if student_tenant:
            if self.tenant_id and self.tenant_id != student_tenant:
                raise ValidationError({"tenant_id": "O tenant da competência do aluno deve coincidir com o tenant do aluno."})
            if not self.tenant_id:
                self.tenant_id = student_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id é obrigatório. Envie o header X-Tenant-ID ou configure tenant_id no seu perfil (UserProfile)."})
        if not 0 <= self.nivel <= 5:
            raise ValidationError({"nivel": "O nível deve estar entre 0.0 e 5.0."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "competency"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_student_competency_active",
            ),
        ]
        verbose_name = "Competência do aluno"
        verbose_name_plural = "Competências dos Alunos"
