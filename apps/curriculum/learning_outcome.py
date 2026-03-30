from django.core.exceptions import ValidationError
# Exceções de validação de domínio do Django.
from django.db import models
# Campos e opções de modelagem.

from core.models import BaseCodeModel
# Modelo base com código, auditoria e soft-delete.
from .subject import Subject
# Referência à disciplina associada ao resultado.


class LearningOutcome(BaseCodeModel):
    """Resultado de aprendizagem ligado a disciplina, classe, ciclo e taxonomia."""

    # Prefixo usado na geração de códigos.
    CODE_PREFIX = "LON"

    # Níveis da taxonomia cognitiva de Bloom (simplificados).
    TAXONOMY_CHOICES = [
        ("remember", "Recordar"),
        ("understand", "Compreender"),
        ("apply", "Aplicar"),
        ("analyze", "Analisar"),
        ("evaluate", "Avaliar"),
        ("create", "Criar"),
    ]

    # Dimensões de conhecimento associadas ao resultado.
    KNOWLEDGE_DIMENSION_CHOICES = [
        ("factual", "Factual"),
        ("conceptual", "Conceptual"),
        ("procedural", "Procedimental"),
        ("metacognitive", "Metacognitiva"),
    ]

    # Código único visível para referência.
    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    # Descrição textual do resultado esperado.
    description = models.TextField(verbose_name="Descrição")
    # Disciplina à qual o resultado pertence.
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name="Disciplina")
    # Classe/ano letivo.
    grade = models.IntegerField(verbose_name="Classe")
    # Ciclo de ensino (1 ou 2).
    cycle = models.IntegerField(verbose_name="Ciclo")
    # Nível da taxonomia escolhido.
    taxonomy_level = models.CharField(max_length=20, choices=TAXONOMY_CHOICES, default="remember", verbose_name="Nível taxonómico")
    # Dimensão do conhecimento associada.
    knowledge_dimension = models.CharField(max_length=20, choices=KNOWLEDGE_DIMENSION_CHOICES, default="factual", verbose_name="Dimensão do conhecimento")
    # Flag de ativação.
    active = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        # Rótulo singular no admin.
        verbose_name = "Resultado de aprendizagem"
        # Rótulo plural no admin.
        verbose_name_plural = "Resultados de aprendizagem"
        # Ordenação por código para consultas consistentes.
        ordering = ["code"]

    def clean(self):
        """Garante que disciplina, classe e ciclo estejam preenchidos."""
        # Confere obrigatoriedade da disciplina.
        if not self.subject_id:
            raise ValidationError({"subject": "Informe a disciplina."})
        # Confere obrigatoriedade da classe.
        if self.grade is None:
            raise ValidationError({"grade": "Informe a classe."})
        # Confere obrigatoriedade do ciclo.
        if self.cycle is None:
            raise ValidationError({"cycle": "Informe o ciclo."})
