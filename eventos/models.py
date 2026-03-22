from django.db import models


class Evento(models.Model):
    TIPO_CHOICES = [
        ('aluno_registrado', 'Aluno Registrado'),
        ('avaliacao_registrada', 'Avaliação Registrada'),
        ('competencia_atualizada', 'Competência Atualizada'),
        ('ciclo_concluido', 'Ciclo Concluído'),
        ('relatorio_gerado', 'Relatório Gerado'),
    ]

    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES, verbose_name="Tipo de Evento")
    data = models.DateTimeField(auto_now_add=True, verbose_name="Data do Evento")
    dados = models.JSONField(verbose_name="Dados do Evento")
    tenant_id = models.CharField(max_length=50, verbose_name="ID do Tenant")

    def __str__(self):
        return f"{self.tipo} at {self.data}"

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ['-data']
