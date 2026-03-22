from django.db import models


class Avaliacao(models.Model):
    TIPO_CHOICES = [
        ('diagnostica', 'Diagnóstica'),
        ('formativa', 'Formativa'),
        ('sumativa', 'Sumativa'),
    ]

    aluno = models.ForeignKey('academico.Aluno', on_delete=models.CASCADE, verbose_name="Aluno")
    competencia = models.ForeignKey('curriculo.Competencia', on_delete=models.CASCADE, verbose_name="Competência")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name="Tipo")
    data = models.DateField(verbose_name="Data")
    nota = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, verbose_name="Nota")  # Optional, since competency-based
    comentario = models.TextField(blank=True, verbose_name="Comentário")
    # For multiformat: could add file or other fields

    # Aspects evaluated
    conhecimentos = models.BooleanField(default=False, verbose_name="Conhecimentos")
    habilidades = models.BooleanField(default=False, verbose_name="Habilidades")
    atitudes = models.BooleanField(default=False, verbose_name="Atitudes")

    def __str__(self):
        return f"Avaliação {self.tipo} de {self.aluno} em {self.competencia}"

    class Meta:
        verbose_name = "Avaliação"
        verbose_name_plural = "Avaliações"
        ordering = ['-data']
