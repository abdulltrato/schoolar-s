from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseCodeModel
from .subject import Subject


class LearningOutcome(BaseCodeModel):
    CODE_PREFIX = "LON"

    TAXONOMY_CHOICES = [
        ("remember", "Recordar"),
        ("understand", "Compreender"),
        ("apply", "Aplicar"),
        ("analyze", "Analisar"),
        ("evaluate", "Avaliar"),
        ("create", "Criar"),
    ]

    KNOWLEDGE_DIMENSION_CHOICES = [
        ("factual", "Factual"),
        ("conceptual", "Conceptual"),
        ("procedural", "Procedimental"),
        ("metacognitive", "Metacognitiva"),
    ]

    code = models.CharField(max_length=20, unique=True, verbose_name="Código")
    description = models.TextField(verbose_name="Descrição")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name="Disciplina")
    grade = models.IntegerField(verbose_name="Classe")
    cycle = models.IntegerField(verbose_name="Ciclo")
    taxonomy_level = models.CharField(max_length=20, choices=TAXONOMY_CHOICES, default="remember", verbose_name="Nível taxonómico")
    knowledge_dimension = models.CharField(max_length=20, choices=KNOWLEDGE_DIMENSION_CHOICES, default="factual", verbose_name="Dimensão do conhecimento")
    active = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        verbose_name = "Resultado de aprendizagem"
        verbose_name_plural = "Resultados de aprendizagem"
        ordering = ["code"]

    def clean(self):
        if not self.subject_id:
            raise ValidationError({"subject": "Informe a disciplina."})
        if self.grade is None:
            raise ValidationError({"grade": "Informe a classe."})
        if self.cycle is None:
            raise ValidationError({"cycle": "Informe o ciclo."})
