from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseCodeModel
from .guardian import Guardian
from .student import Student


class StudentGuardian(BaseCodeModel):
    CODE_PREFIX = "STG"

    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="Aluno")
    guardian = models.ForeignKey(Guardian, on_delete=models.CASCADE, verbose_name="Encarregado")
    primary_contact = models.BooleanField(default=False, verbose_name="Contato principal")
    receives_notifications = models.BooleanField(default=True, verbose_name="Recebe notificações")

    def clean(self):
        student_tenant = (self.student.tenant_id or "").strip()
        guardian_tenant = getattr(self.guardian, "tenant_id", "") or ""
        guardian_tenant = guardian_tenant.strip()
        if student_tenant and guardian_tenant and student_tenant != guardian_tenant:
            raise ValidationError("Aluno e encarregado devem pertencer ao mesmo tenant.")
        if self.tenant_id and student_tenant and self.tenant_id != student_tenant:
            raise ValidationError({"tenant_id": "O tenant do vínculo aluno-encarregado deve coincidir com o tenant do aluno."})
        if self.tenant_id and guardian_tenant and self.tenant_id != guardian_tenant:
            raise ValidationError({"tenant_id": "O tenant do vínculo aluno-encarregado deve coincidir com o tenant do encarregado."})
        self.tenant_id = self.tenant_id or student_tenant or guardian_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id é obrigatório. Envie o header X-Tenant-ID ou configure tenant_id no seu perfil (UserProfile)."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.guardian} - {self.student}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "student", "guardian"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_student_guardian_active",
            ),
        ]
        verbose_name = "Relação aluno-encarregado"
        verbose_name_plural = "Relações aluno-encarregado"
