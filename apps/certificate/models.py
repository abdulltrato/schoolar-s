from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from core.models import BaseCodeModel


class Certificate(BaseCodeModel):
    CODE_PREFIX = "CRT"
    STATUS_CHOICES = [
        ("draft", "Rascunho"),
        ("issued", "Emitido"),
    ]

    student = models.ForeignKey("academic.Student", on_delete=models.CASCADE, verbose_name="Aluno")
    course = models.ForeignKey("learning.Course", on_delete=models.CASCADE, verbose_name="Curso")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft", verbose_name="Estado")
    issued_at = models.DateTimeField(null=True, blank=True, verbose_name="Emitido em")
    notes = models.TextField(blank=True, verbose_name="Observações")

    def clean(self):
        student_tenant = (self.student.tenant_id or "").strip() if self.student_id else ""
        course_tenant = (self.course.tenant_id or "").strip() if self.course_id else ""
        if student_tenant and course_tenant and student_tenant != course_tenant:
            raise ValidationError({"course": "O curso e o aluno devem pertencer ao mesmo tenant."})
        self.ensure_tenant(student_tenant, course_tenant, self.tenant_id)

    def save(self, *args, **kwargs):
        if self.status == "issued" and not self.issued_at:
            self.issued_at = timezone.now()
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.course} ({self.get_status_display()})"


class CertificateExamRecord(BaseCodeModel):
    CODE_PREFIX = "CER"
    certificate = models.ForeignKey(
        Certificate,
        on_delete=models.CASCADE,
        related_name="records",
        verbose_name="Certificado",
    )
    assessment = models.ForeignKey(
        "assessment.Assessment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Avaliação",
    )
    subject = models.ForeignKey("curriculum.Subject", on_delete=models.PROTECT, verbose_name="Disciplina")
    exam_type = models.CharField(max_length=40, verbose_name="Tipo de exame")
    score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Nota")
    exam_date = models.DateField(null=True, blank=True, verbose_name="Data do exame")

    def clean(self):
        certificate_tenant = (self.certificate.tenant_id or "").strip() if self.certificate_id else ""
        subject_tenant = (self.subject.tenant_id or "").strip() if self.subject_id else ""
        if subject_tenant and certificate_tenant and subject_tenant != certificate_tenant:
            raise ValidationError({"subject": "A disciplina deve pertencer ao mesmo tenant do certificado."})
        self.ensure_tenant(certificate_tenant, subject_tenant, self.tenant_id)

    def __str__(self):
        return f"{self.subject} - {self.score}"
