from __future__ import annotations
# Suporte a anotações forward.

from django.apps import apps
# Utilitário para resolver modelos dinamicamente.
from django.core.exceptions import ValidationError
# Exceção de validação.
from django.db import models
# Componentes do ORM.

from core.models import BaseCodeModel
# Modelo base com código e auditoria.
from .models_courses import CourseOffering
# Oferta de curso relacionada às tarefas.


class Assignment(BaseCodeModel):
    """Tarefa/atividade publicada em uma oferta de curso."""

    CODE_PREFIX = "ASN"
    offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, related_name="assignments", verbose_name="Oferta")
    title = models.CharField(max_length=180, verbose_name="Título")
    instructions = models.TextField(blank=True, verbose_name="Instruções")
    opens_at = models.DateTimeField(verbose_name="Abre em")
    due_at = models.DateTimeField(verbose_name="Prazo")
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=20, verbose_name="Nota máxima")
    published = models.BooleanField(default=False, verbose_name="Publicada")

    def clean(self):
        """Valida tenant, datas de abertura/prazo e coerência com a oferta."""
        offering_tenant = (self.offering.tenant_id or "").strip() if self.offering_id else ""
        if self.tenant_id and offering_tenant and self.tenant_id != offering_tenant:
            raise ValidationError({"tenant_id": "O tenant da tarefa deve coincidir com o tenant da oferta."})
        if offering_tenant and not self.tenant_id:
            self.tenant_id = offering_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id é obrigatório. Envie o header X-Tenant-ID ou configure tenant_id no seu perfil (UserProfile)."})
        if self.opens_at and self.due_at and self.due_at <= self.opens_at:
            raise ValidationError({"due_at": "O prazo deve ser posterior à data de abertura."})

    def save(self, *args, **kwargs):
        """Valida antes de persistir."""
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Tarefa"
        verbose_name_plural = "Tarefas"
        ordering = ["-due_at"]


class Submission(BaseCodeModel):
    """Entrega de um aluno para uma tarefa, com nota e feedback."""

    CODE_PREFIX = "SBM"
    STATUS_CHOICES = [
        ("draft", "Rascunho"),
        ("submitted", "Submetida"),
        ("graded", "Corrigida"),
    ]

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="submissions", verbose_name="Tarefa")
    student = models.ForeignKey("academic.Student", on_delete=models.CASCADE, verbose_name="Aluno")
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name="Submetida em")
    text_response = models.TextField(blank=True, verbose_name="Resposta")
    attachment_url = models.URLField(blank=True, verbose_name="Link do anexo")
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Nota")
    feedback = models.TextField(blank=True, verbose_name="Devolutiva")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft", verbose_name="Estado")

    def clean(self):
        """Valida tenant, nota máxima e se aluno está vinculado à turma/curso."""
        assignment_tenant = (self.assignment.tenant_id or "").strip() if self.assignment_id else ""
        student_tenant = (self.student.tenant_id or "").strip() if self.student_id else ""
        if assignment_tenant and student_tenant and assignment_tenant != student_tenant:
            raise ValidationError({"tenant_id": "A tarefa e o aluno devem pertencer ao mesmo tenant."})
        if self.tenant_id and assignment_tenant and self.tenant_id != assignment_tenant:
            raise ValidationError({"tenant_id": "O tenant da submissão deve coincidir com o tenant da tarefa."})
        if self.tenant_id and student_tenant and self.tenant_id != student_tenant:
            raise ValidationError({"tenant_id": "O tenant da submissão deve coincidir com o tenant do aluno."})
        self.tenant_id = self.tenant_id or assignment_tenant or student_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id é obrigatório. Envie o header X-Tenant-ID ou configure tenant_id no seu perfil (UserProfile)."})
        if self.score is not None and self.score > self.assignment.max_score:
            raise ValidationError({"score": "A nota não pode exceder a nota máxima da tarefa."})
        if self.assignment_id and self.student_id:
            offering = self.assignment.offering
            if offering.classroom_id:
                Enrollment = apps.get_model("school", "Enrollment")
                enrolled = Enrollment.objects.filter(student=self.student, classroom=offering.classroom).exists()
                linked_to_course = False
                try:
                    linked_to_course = offering.course and offering.course.students.filter(pk=self.student_id).exists()
                except Exception:
                    linked_to_course = False
                if not enrolled and not linked_to_course:
                    raise ValidationError({"student": "O aluno deve estar matriculado na turma da oferta."})

    def save(self, *args, **kwargs):
        """Valida antes de salvar."""
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.assignment} - {self.student}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["assignment", "student"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_submission_active",
            ),
        ]
        verbose_name = "Submissão"
        verbose_name_plural = "Submissões"
        ordering = ["-submitted_at"]


class SubmissionAttachment(BaseCodeModel):
    """Anexo de arquivo para uma submissão de tarefa."""

    CODE_PREFIX = "SAT"
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="Submissão",
    )
    title = models.CharField(max_length=180, verbose_name="Nome do arquivo")
    description = models.TextField(blank=True, verbose_name="Descrição")
    file = models.FileField(upload_to="submission_attachments/", verbose_name="Arquivo")
    enabled = models.BooleanField(default=True, verbose_name="Usar este arquivo")

    def clean(self):
        """Herda tenant da submissão e exige arquivo quando habilitado."""
        submission_tenant = (self.submission.tenant_id or "").strip() if self.submission_id else ""
        if submission_tenant:
            if self.tenant_id and self.tenant_id != submission_tenant:
                raise ValidationError({"tenant_id": "O tenant do anexo deve coincidir com o da submissão."})
            if not self.tenant_id:
                self.tenant_id = submission_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id é obrigatório."})
        if self.enabled and not self.file:
            raise ValidationError({"file": "Envie o arquivo ou desmarque o anexo."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title
