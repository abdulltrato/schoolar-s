from django.core.exceptions import ValidationError
# Exceção de validação.
from django.db import models
# Campos do ORM.

from core.models import BaseCodeModel
# Modelo base com código e auditoria.

from .classroom import Classroom
# Turma para a qual o docente é alocado.
from .grade_subject import GradeSubject
# Disciplina ofertada em uma classe.
from .teacher import Teacher
# Professor alocado.


class TeachingAssignment(BaseCodeModel):
    """Alocação de professor para lecionar uma disciplina em determinada turma."""

    CODE_PREFIX = "TAS"

    # Professor designado.
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="Professor")
    # Turma alvo.
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, verbose_name="Turma")
    # Disciplina da classe (ano letivo + classe + disciplina).
    grade_subject = models.ForeignKey(GradeSubject, on_delete=models.CASCADE, verbose_name="Disciplina da classe")

    def clean(self):
        """Valida tenants e garante que turma, disciplina e professor combinam."""
        if self.classroom_id and self.grade_subject_id:
            teacher_tenant = (self.teacher.tenant_id or "").strip()
            classroom_tenant = (self.classroom.tenant_id or "").strip()
            grade_subject_tenant = (self.grade_subject.tenant_id or "").strip()
            if teacher_tenant and classroom_tenant and teacher_tenant != classroom_tenant:
                raise ValidationError({"tenant_id": "Professor e turma devem pertencer ao mesmo tenant."})
            if grade_subject_tenant and classroom_tenant and grade_subject_tenant != classroom_tenant:
                raise ValidationError({"tenant_id": "Disciplina da classe e turma devem pertencer ao mesmo tenant."})
            if grade_subject_tenant and teacher_tenant and grade_subject_tenant != teacher_tenant:
                raise ValidationError({"tenant_id": "Disciplina da classe e professor devem pertencer ao mesmo tenant."})
            if self.tenant_id and teacher_tenant and self.tenant_id != teacher_tenant:
                raise ValidationError({"tenant_id": "O tenant da alocação deve coincidir com o tenant do professor."})
            if self.tenant_id and classroom_tenant and self.tenant_id != classroom_tenant:
                raise ValidationError({"tenant_id": "O tenant da alocação deve coincidir com o tenant da turma."})
            if self.tenant_id and grade_subject_tenant and self.tenant_id != grade_subject_tenant:
                raise ValidationError({"tenant_id": "O tenant da alocação deve coincidir com o tenant da disciplina da classe."})
            self.tenant_id = self.tenant_id or teacher_tenant or classroom_tenant or grade_subject_tenant
            if self.classroom.grade_id != self.grade_subject.grade_id:
                raise ValidationError({"grade_subject": "A disciplina deve pertencer à classe da turma."})
            if self.classroom.academic_year_id != self.grade_subject.academic_year_id:
                raise ValidationError({"grade_subject": "A disciplina deve pertencer ao mesmo ano letivo da turma."})
            if self.teacher.school_id and self.classroom.school_id and self.teacher.school_id != self.classroom.school_id:
                raise ValidationError({"teacher": "O professor deve pertencer à mesma escola da turma."})

    def save(self, *args, **kwargs):
        """Valida antes de salvar."""
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        """Exibe professor, disciplina e turma."""
        return f"{self.teacher} - {self.grade_subject.subject} - {self.classroom}"

    class Meta:
        verbose_name = "Alocação docente"
        verbose_name_plural = "Alocações docentes"
        ordering = ["classroom__academic_year__code", "classroom__name", "grade_subject__subject__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["classroom", "grade_subject"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_teaching_assignment_active",
            ),
        ]
