from django.db import models


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
    # For aluno
    aluno = models.ForeignKey('academico.Aluno', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Aluno")
    # For escola: tenant is implicit
    # Nacional: no specific

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Relatório"
        verbose_name_plural = "Relatórios"
        ordering = ['-data_geracao']
