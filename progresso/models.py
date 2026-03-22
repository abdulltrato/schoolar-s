from django.db import models


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
    # Based on competencies: perhaps link to average or specific checks

    def __str__(self):
        return f"Progressão {self.aluno} Ciclo {self.ciclo} - {self.decisao}"

    class Meta:
        verbose_name = "Progressão"
        verbose_name_plural = "Progressões"
        ordering = ['-data_decisao']
