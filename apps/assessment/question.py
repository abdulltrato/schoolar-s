from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseCodeModel


class Question(BaseCodeModel):
    CODE_PREFIX = "QUZ"
    TYPE_CHOICES = [
        ("test", "Teste"),
        ("exam", "Exame"),
        ("acs", "ACS"),
        ("acp", "ACP"),
    ]

    subject = models.ForeignKey(
        "curriculum.Subject",
        on_delete=models.CASCADE,
        verbose_name="Disciplina",
    )
    question_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Tipo")
    text = models.TextField(verbose_name="Pergunta")
    vocational = models.BooleanField(default=False, verbose_name="Conteúdo vocacional")

    def clean(self):
        subject_tenant = (self.subject.tenant_id or "").strip() if self.subject_id else ""
        if subject_tenant:
            if self.tenant_id and self.tenant_id != subject_tenant:
                raise ValidationError({"tenant_id": "O tenant da pergunta deve coincidir com o tenant da disciplina."})
            if not self.tenant_id:
                self.tenant_id = subject_tenant

    def __str__(self):
        return f"{self.subject} - {self.question_type}"


class AssessmentQuestion(BaseCodeModel):
    CODE_PREFIX = "AQS"
    assessment = models.ForeignKey(
        "assessment.Assessment",
        on_delete=models.CASCADE,
        related_name="question_links",
        verbose_name="Avaliação",
    )
    question = models.ForeignKey(Question, on_delete=models.PROTECT, verbose_name="Pergunta")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="Ordem")

    class Meta:
        ordering = ("order",)
        constraints = [
            models.UniqueConstraint(
                fields=["assessment", "question"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_assessment_question_active",
            ),
        ]

    def __str__(self):
        return f"{self.assessment} - {self.question}"
