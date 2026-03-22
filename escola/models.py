from django.db import models
from django.contrib.auth.models import User


class Professor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Usuário")
    nome = models.CharField(max_length=100, verbose_name="Nome")
    especialidade = models.CharField(max_length=100, blank=True, verbose_name="Especialidade")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Professor"
        verbose_name_plural = "Professores"
        ordering = ['nome']


class Turma(models.Model):
    nome = models.CharField(max_length=50, verbose_name="Nome")
    ciclo = models.IntegerField(verbose_name="Ciclo")
    ano_letivo = models.CharField(max_length=10, verbose_name="Ano Letivo")
    professor_responsavel = models.ForeignKey(Professor, on_delete=models.SET_NULL, null=True, verbose_name="Professor Responsável")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Turma"
        verbose_name_plural = "Turmas"
        ordering = ['nome']


class Matricula(models.Model):
    aluno = models.ForeignKey('academico.Aluno', on_delete=models.CASCADE, verbose_name="Aluno")
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, verbose_name="Turma")
    data_matricula = models.DateField(auto_now_add=True, verbose_name="Data da Matrícula")

    class Meta:
        unique_together = ('aluno', 'turma')
        verbose_name = "Matrícula"
        verbose_name_plural = "Matrículas"
        ordering = ['-data_matricula']

    def __str__(self):
        return f"Matrícula de {self.aluno} na {self.turma}"
