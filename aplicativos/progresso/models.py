from django.db import models
from django.core.exceptions import ValidationError
import re


class Progressao(models.Model):
    DECISAO_CHOICES = [
        ('aprovado', 'Aprovado'),
        ('retido', 'Retido'),
        ('transferido', 'Transferido'),
    ]

    aluno = models.ForeignKey('academico.Aluno', on_delete=models.CASCADE, verbose_name="Aluno")
    ciclo = models.IntegerField(verbose_name="Ciclo")
    ano_letivo = models.CharField(max_length=10, verbose_name="Ano Letivo")  # e.g., '2023-2024'
    data_decisao = models.DateField(verbose_name="Data da Decisão")
    decisao = models.CharField(max_length=20, choices=DECISAO_CHOICES, verbose_name="Decisão")
    comentario = models.TextField(blank=True, verbose_name="Comentário")

    def clean(self):
        if self.ciclo not in {1, 2}:
            raise ValidationError({"ciclo": "O ciclo da progressão deve ser 1 ou 2."})
        if self.aluno_id and self.aluno.ciclo != self.ciclo:
            raise ValidationError({"ciclo": "A progressão deve usar o mesmo ciclo do aluno."})
        if not re.fullmatch(r"\d{4}-\d{4}", self.ano_letivo):
            raise ValidationError({"ano_letivo": "Use o formato AAAA-AAAA."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Progressão {self.aluno} Ciclo {self.ciclo} - {self.decisao}"

    class Meta:
        verbose_name = "Progressão"
        verbose_name_plural = "Progressões"
        ordering = ['-data_decisao']
