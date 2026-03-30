from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseCodeModel
from .guardian import Guardian
from .student import Student


# Modelo que vincula um aluno a um encarregado.
class StudentGuardian(BaseCodeModel):
    """Relação aluno-encarregado, com flags de contato principal e notificações."""
    # Prefixo para códigos automáticos.
    CODE_PREFIX = "STG"

    # FK para o aluno.
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="Aluno")
    # FK para o encarregado.
    guardian = models.ForeignKey(Guardian, on_delete=models.CASCADE, verbose_name="Encarregado")
    # Indica se é o contato principal.
    primary_contact = models.BooleanField(default=False, verbose_name="Contato principal")
    # Define se recebe notificações.
    receives_notifications = models.BooleanField(default=True, verbose_name="Recebe notificações")

    def clean(self):
        # Extrai tenant do aluno.
        student_tenant = (self.student.tenant_id or "").strip()
        # Extrai tenant do encarregado.
        guardian_tenant = getattr(self.guardian, "tenant_id", "") or ""
        guardian_tenant = guardian_tenant.strip()
        # Exige que aluno e encarregado compartilhem o mesmo tenant.
        if student_tenant and guardian_tenant and student_tenant != guardian_tenant:
            raise ValidationError("Aluno e encarregado devem pertencer ao mesmo tenant.")
        # Valida coerência entre tenant da instância e do aluno.
        if self.tenant_id and student_tenant and self.tenant_id != student_tenant:
            raise ValidationError({"tenant_id": "O tenant do vínculo aluno-encarregado deve coincidir com o tenant do aluno."})
        # Valida coerência entre tenant da instância e do encarregado.
        if self.tenant_id and guardian_tenant and self.tenant_id != guardian_tenant:
            raise ValidationError({"tenant_id": "O tenant do vínculo aluno-encarregado deve coincidir com o tenant do encarregado."})
        # Preenche tenant com o primeiro valor disponível.
        self.tenant_id = self.tenant_id or student_tenant or guardian_tenant
        # Garante que o tenant foi definido.
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id é obrigatório. Envie o header X-Tenant-ID ou configure tenant_id no seu perfil (UserProfile)."})

    def save(self, *args, **kwargs):
        # Valida antes de salvar.
        self.full_clean()
        # Salva com comportamento padrão.
        return super().save(*args, **kwargs)

    def __str__(self):
        # Representação legível no admin e logs.
        return f"{self.guardian} - {self.student}"

    class Meta:
        # Garante unicidade do vínculo ativo por tenant.
        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "student", "guardian"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_student_guardian_active",
            ),
        ]
        # Metadados de exibição.
        verbose_name = "Relação aluno-encarregado"
        verbose_name_plural = "Relações aluno-encarregado"
