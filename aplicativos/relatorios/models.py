from django.db import models
from django.core.exceptions import ValidationError


class Relatorio(models.Model):
    TIPO_CHOICES = [
        ('aluno', 'Relatório de Aluno'),
        ('escola', 'Relatório de Escola'),
        ('nacional', 'Relatório Nacional'),
    ]

    titulo = models.CharField(max_length=200, verbose_name="Título")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name="Tipo")
    data_geracao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Geração")
    periodo = models.CharField(max_length=50, blank=True, verbose_name="Período")  # e.g., '2023-2024'
    conteudo = models.JSONField(verbose_name="Conteúdo")  # Store report data as JSON
    aluno = models.ForeignKey('academico.Aluno', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Aluno")

    def clean(self):
        if self.tipo == "aluno" and not self.aluno_id:
            raise ValidationError({"aluno": "Relatórios de aluno exigem um aluno associado."})
        if self.tipo != "aluno" and self.aluno_id:
            raise ValidationError({"aluno": "Apenas relatórios do tipo aluno podem referenciar um aluno."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Relatório"
        verbose_name_plural = "Relatórios"
        ordering = ['-data_geracao']
