from __future__ import annotations
# Suporte a anotações forward.

from django.core.exceptions import ValidationError
# Exceção de validação.
from django.db import models
# Componentes do ORM.
from django.utils import timezone
# Utilitários de data/hora.

from core.models import BaseCodeModel
# Modelo base com código e auditoria.
from core.request_context import get_current_request
# Permite acessar o request atual para obter o usuário.
from .apply_student import apply_student_transfer
# Executor de transferência de aluno.
from .apply_teacher import apply_teacher_transfer
# Executor de transferência de professor.
from .validators import validate_student_transfer, validate_teacher_transfer
# Validadores específicos de cada tipo de transferência.


class Transfer(BaseCodeModel):
    """Solicitação de transferência de aluno ou professor entre escolas/turmas."""

    CODE_PREFIX = "TRF"

    KIND_CHOICES = [
        ("student", "Aluno"),
        ("teacher", "Professor"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pendente"),
        ("applied", "Aplicada"),
        ("failed", "Falhou"),
        ("canceled", "Cancelada"),
    ]

    # Tipo de sujeito (aluno ou professor).
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, verbose_name="Tipo")
    # Aluno transferido (exclusivo para kind=student).
    student = models.ForeignKey("academic.Student", on_delete=models.PROTECT, null=True, blank=True, related_name="transfers", verbose_name="Aluno")
    # Professor transferido (exclusivo para kind=teacher).
    teacher = models.ForeignKey("school.Teacher", on_delete=models.PROTECT, null=True, blank=True, related_name="transfers", verbose_name="Professor")
    # Escola de origem e destino.
    from_school = models.ForeignKey("school.School", on_delete=models.SET_NULL, null=True, blank=True, related_name="+", verbose_name="Escola de origem")
    to_school = models.ForeignKey("school.School", on_delete=models.SET_NULL, null=True, blank=True, related_name="+", verbose_name="Escola de destino")
    # Turma de origem/destino (alunos) ou onde o professor atua.
    from_classroom = models.ForeignKey("school.Classroom", on_delete=models.SET_NULL, null=True, blank=True, related_name="+", verbose_name="Turma de origem")
    to_classroom = models.ForeignKey("school.Classroom", on_delete=models.SET_NULL, null=True, blank=True, related_name="+", verbose_name="Turma de destino")
    # Nova especialidade (para transferências de professor).
    new_specialty = models.ForeignKey("curriculum.SubjectSpecialty", on_delete=models.PROTECT, null=True, blank=True, related_name="+", verbose_name="Nova especialidade")
    # Se verdadeiro, move alocações docentes junto com o professor.
    move_teaching_assignments = models.BooleanField(default=False, verbose_name="Mover alocações docentes")
    # Motivo textual.
    reason = models.TextField(blank=True, verbose_name="Motivo")
    # Estado da solicitação.
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="Estado")
    # Timestamp de aplicação.
    applied_at = models.DateTimeField(null=True, blank=True, verbose_name="Aplicada em")
    # Mensagem de erro, quando houver.
    error_message = models.TextField(blank=True, verbose_name="Erro")

    class Meta:
        verbose_name = "Transferência"
        verbose_name_plural = "Transferências"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        subject = self.student or self.teacher
        return f"{self.get_kind_display()} - {subject or self.pk}"

    def save(self, *args, **kwargs):
        """Valida antes de persistir."""
        self.full_clean()
        return super().save(*args, **kwargs)

    def _resolve_actor(self):
        """Obtém usuário autenticado do request atual (se existir)."""
        request = get_current_request()
        user = getattr(request, "user", None) if request else None
        if user and getattr(user, "is_authenticated", False):
            return user
        return None

    def _resolve_source_tenant(self) -> str:
        """Determina tenant de origem a partir do aluno ou professor."""
        if self.kind == "student" and self.student_id:
            return (getattr(self.student, "tenant_id", "") or "").strip()
        if self.kind == "teacher" and self.teacher_id:
            return (getattr(self.teacher, "tenant_id", "") or "").strip()
        return ""

    def _resolve_target_tenant(self) -> str:
        """Determina tenant de destino a partir da turma ou escola de destino."""
        if self.to_classroom_id:
            return (getattr(self.to_classroom, "tenant_id", "") or "").strip()
        if self.to_school_id:
            return (getattr(self.to_school, "tenant_id", "") or "").strip()
        return ""

    def clean(self):
        """Valida tipo, regras específicas e permissões de transferência entre tenants."""
        self.kind = (self.kind or "").strip()
        self.status = (self.status or "").strip() or "pending"

        if self.kind not in {"student", "teacher"}:
            raise ValidationError({"kind": "Tipo inválido."})

        if self.kind == "student":
            validate_student_transfer(self)
        else:
            validate_teacher_transfer(self)

        source_tenant = self._resolve_source_tenant()
        if not source_tenant:
            raise ValidationError({"tenant_id": "Não foi possível determinar o tenant de origem."})

        target_tenant = self._resolve_target_tenant()
        if not target_tenant:
            raise ValidationError({"to_school": "Não foi possível determinar o tenant de destino."})

        if not (self.tenant_id or "").strip():
            self.tenant_id = source_tenant

        if target_tenant != source_tenant:
            actor = self._resolve_actor()
            profile = getattr(actor, "school_profile", None) if actor else None
            role = getattr(profile, "role", None) if profile else None
            if role not in {"national_admin", "provincial_admin", "district_admin"}:
                raise ValidationError({"to_school": "A transferência entre tenants requer perfil de administrador."})

        if self.kind == "student" and self.from_classroom_id:
            from apps.school.models import Enrollment

            enrolled = Enrollment.objects.filter(
                student_id=self.student_id,
                classroom_id=self.from_classroom_id,
                deleted_at__isnull=True,
            ).exists()
            if not enrolled:
                raise ValidationError({"from_classroom": "O aluno não está matriculado na turma de origem."})

        if self.kind == "teacher" and self.from_classroom_id:
            current_lead = getattr(self.from_classroom, "lead_teacher_id", None)
            if current_lead and current_lead != self.teacher_id:
                raise ValidationError({"from_classroom": "O professor não é o diretor da turma de origem."})

    def apply(self):
        """Executa a transferência pendente e marca como aplicada."""
        if self.status != "pending":
            raise ValidationError({"status": "Só é possível aplicar transferências pendentes."})

        actor = self._resolve_actor()
        now = timezone.now()

        if self.kind == "student":
            apply_student_transfer(self, actor=actor)
        else:
            apply_teacher_transfer(self, actor=actor)

        type(self).objects.filter(pk=self.pk).update(
            status="applied",
            applied_at=now,
            error_message="",
            updated_at=now,
        )
        self.status = "applied"
        self.applied_at = now
        self.error_message = ""
