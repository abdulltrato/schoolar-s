from django.db import models
from django.core.exceptions import ValidationError


class Aluno(models.Model):
    CICLO_CHOICES = [
        (1, '1º Ciclo'),
        (2, '2º Ciclo'),
    ]

    ESTADO_CHOICES = [
        ('ativo', 'Ativo'),
        ('graduado', 'Graduado'),
        ('retido', 'Retido'),
        ('transferido', 'Transferido'),
    ]

    nome = models.CharField(max_length=100, verbose_name="Nome")
    data_nascimento = models.DateField(verbose_name="Data de Nascimento")
    classe = models.IntegerField(verbose_name="Classe")  # 1 to 6
    ciclo = models.IntegerField(choices=CICLO_CHOICES, verbose_name="Ciclo")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ativo', verbose_name="Estado")
    competencias = models.ManyToManyField('curriculo.Competencia', through='AlunoCompetencia', verbose_name="Competências")

    def clean(self):
        if not 1 <= self.classe <= 6:
            raise ValidationError({"classe": "A classe deve estar entre 1 e 6."})
        ciclo_esperado = 1 if self.classe <= 3 else 2
        if self.ciclo != ciclo_esperado:
            raise ValidationError({"ciclo": "O ciclo deve corresponder à classe do aluno."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"
        ordering = ['nome']


class AlunoCompetencia(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, verbose_name="Aluno")
    competencia = models.ForeignKey('curriculo.Competencia', on_delete=models.CASCADE, verbose_name="Competência")
    nivel = models.DecimalField(max_digits=3, decimal_places=1, default=0.0, verbose_name="Nível")  # e.g., 0.0 to 5.0
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")

    def clean(self):
        if not 0 <= self.nivel <= 5:
            raise ValidationError({"nivel": "O nível deve estar entre 0.0 e 5.0."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        unique_together = ('aluno', 'competencia')
        verbose_name = "Competência do Aluno"
        verbose_name_plural = "Competências dos Alunos"
