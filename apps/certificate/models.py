from django.core.exceptions import ValidationError
# Exceção usada para validações de domínio.
from django.db import models
# Campos e tipos do ORM do Django.
from django.utils import timezone
# Utilitário para timestamps atuais.

from core.models import BaseCodeModel
# Modelo base com código, auditoria e soft-delete.
from core.tenant_mixins import TenantValidationMixin
# Mixin que centraliza validação de tenant.


class Certificate(BaseCodeModel, TenantValidationMixin):
    """Certificado emitido para um aluno em determinado curso, com controle de tenant e estado."""

    # Prefixo de código gerado automaticamente.
    CODE_PREFIX = "CRT"
    # Estados possíveis do certificado.
    STATUS_CHOICES = [
        ("draft", "Rascunho"),
        ("issued", "Emitido"),
    ]

    # Aluno beneficiário do certificado.
    student = models.ForeignKey("academic.Student", on_delete=models.CASCADE, verbose_name="Aluno")
    # Curso concluído que originou o certificado.
    course = models.ForeignKey("learning.Course", on_delete=models.CASCADE, verbose_name="Curso")
    # Estado atual do certificado.
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft", verbose_name="Estado")
    # Momento de emissão; preenchido automaticamente ao emitir.
    issued_at = models.DateTimeField(null=True, blank=True, verbose_name="Emitido em")
    # Observações livres.
    notes = models.TextField(blank=True, verbose_name="Observações")

    def clean(self):
        """Valida consistência de tenant entre aluno, curso e certificado."""
        # Obtém tenant do aluno se já estiver associado.
        student_tenant = (self.student.tenant_id or "").strip() if self.student_id else ""
        # Obtém tenant do curso se já estiver associado.
        course_tenant = (self.course.tenant_id or "").strip() if self.course_id else ""
        # Impede mismatch de tenant entre aluno e curso.
        if student_tenant and course_tenant and student_tenant != course_tenant:
            raise ValidationError({"course": "O curso e o aluno devem pertencer ao mesmo tenant."})
        # Se qualquer tenant estiver presente, delega validação ao mixin.
        if student_tenant or course_tenant or (self.tenant_id or "").strip():
            self.ensure_tenant(student_tenant, course_tenant, self.tenant_id)

    def save(self, *args, **kwargs):
        """Preenche issued_at quando status é emitido e executa validações antes de salvar."""
        # Define timestamp de emissão caso ainda não exista.
        if self.status == "issued" and not self.issued_at:
            self.issued_at = timezone.now()
        # Executa validações de domínio.
        self.full_clean()
        # Persiste registro usando a lógica de BaseCodeModel.
        return super().save(*args, **kwargs)

    def __str__(self):
        # Representação textual com aluno, curso e status legível.
        return f"{self.student} - {self.course} ({self.get_status_display()})"


class CertificateExamRecord(BaseCodeModel, TenantValidationMixin):
    """Registro de exame que compõe um certificado, referenciando disciplina e nota."""

    # Prefixo de código gerado automaticamente.
    CODE_PREFIX = "CER"
    # Certificado ao qual este registro pertence.
    certificate = models.ForeignKey(
        Certificate,
        on_delete=models.CASCADE,
        related_name="records",
        verbose_name="Certificado",
    )
    # Avaliação opcional associada (pode ser removida posteriormente).
    assessment = models.ForeignKey(
        "assessment.Assessment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Avaliação",
    )
    # Disciplina do exame registrado.
    subject = models.ForeignKey("curriculum.Subject", on_delete=models.PROTECT, verbose_name="Disciplina")
    # Tipo de exame (legado ou atual).
    exam_type = models.CharField(max_length=40, verbose_name="Tipo de exame")
    # Nota obtida.
    score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Nota")
    # Data do exame.
    exam_date = models.DateField(null=True, blank=True, verbose_name="Data do exame")

    def clean(self):
        """Valida consistência de tenant entre certificado, disciplina e o próprio registro."""
        # Tenant do certificado associado.
        certificate_tenant = (self.certificate.tenant_id or "").strip() if self.certificate_id else ""
        # Tenant da disciplina associada.
        subject_tenant = (self.subject.tenant_id or "").strip() if self.subject_id else ""
        # Impede mismatch entre certificado e disciplina.
        if subject_tenant and certificate_tenant and subject_tenant != certificate_tenant:
            raise ValidationError({"subject": "A disciplina deve pertencer ao mesmo tenant do certificado."})
        # Usa mixin para validar/preencher tenant.
        if subject_tenant or certificate_tenant or (self.tenant_id or "").strip():
            self.ensure_tenant(certificate_tenant, subject_tenant, self.tenant_id)

    def __str__(self):
        # Exibe disciplina e nota para facilitar leitura.
        return f"{self.subject} - {self.score}"
