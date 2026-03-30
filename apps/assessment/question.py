from django.core.exceptions import ValidationError
# Importa exceção de validação do Django.
from django.db import models
# Importa campos e base do ORM.

from core.models import BaseCodeModel
# Modelo base com código/tenant.


class Question(BaseCodeModel):
    """Pergunta de avaliação vinculada a uma disciplina e tipo (teste, exame, etc.)."""

    # Prefixo de código para geração automática.
    CODE_PREFIX = "QUZ"
    # Tipos aceitos de pergunta.
    TYPE_CHOICES = [
        ("test", "Teste"),
        ("exam", "Exame"),
        ("acs", "ACS"),
        ("acp", "ACP"),
    ]

    # Disciplina à qual a pergunta pertence.
    subject = models.ForeignKey(
        "curriculum.Subject",
        on_delete=models.CASCADE,
        verbose_name="Disciplina",
    )
    # Tipo da pergunta, alinhado ao tipo de avaliação.
    question_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Tipo")
    # Enunciado da pergunta.
    text = models.TextField(verbose_name="Pergunta")
    # Indica se o conteúdo é vocacional.
    vocational = models.BooleanField(default=False, verbose_name="Conteúdo vocacional")

    def clean(self):
        # Obtém tenant da disciplina para validar consistência.
        subject_tenant = (self.subject.tenant_id or "").strip() if self.subject_id else ""
        if subject_tenant:
            # Exige que tenant da pergunta coincida com o da disciplina.
            if self.tenant_id and self.tenant_id != subject_tenant:
                raise ValidationError({"tenant_id": "O tenant da pergunta deve coincidir com o tenant da disciplina."})
            # Herda tenant da disciplina quando não fornecido.
            if not self.tenant_id:
                self.tenant_id = subject_tenant

    def __str__(self):
        # Exibição rápida no admin/listas.
        return f"{self.subject} - {self.question_type}"


class AssessmentQuestion(BaseCodeModel):
    """Ligação entre avaliação e pergunta, preservando ordem de aplicação."""

    # Prefixo de código para registros desta relação.
    CODE_PREFIX = "AQS"
    # FK para a avaliação que receberá a pergunta.
    assessment = models.ForeignKey(
        "assessment.Assessment",
        on_delete=models.CASCADE,
        related_name="question_links",
        verbose_name="Avaliação",
    )
    # FK para a pergunta selecionada.
    question = models.ForeignKey(Question, on_delete=models.PROTECT, verbose_name="Pergunta")
    # Posição da pergunta na prova/listagem.
    order = models.PositiveSmallIntegerField(default=0, verbose_name="Ordem")

    class Meta:
        # Ordena por ordem definida.
        ordering = ("order",)
        # Impede associação duplicada ativa da mesma pergunta na mesma avaliação.
        constraints = [
            models.UniqueConstraint(
                fields=["assessment", "question"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_assessment_question_active",
            ),
        ]

    def __str__(self):
        # Representação curta da ligação.
        return f"{self.assessment} - {self.question}"
