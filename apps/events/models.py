from django.db import models


class Event(models.Model):
    TYPE_CHOICES = [
        ("student_registered", "Aluno registado"),
        ("assessment_recorded", "Avaliação registada"),
        ("competency_updated", "Competência atualizada"),
        ("cycle_completed", "Ciclo concluído"),
        ("report_generated", "Relatório gerado"),
    ]

    type = models.CharField(max_length=50, choices=TYPE_CHOICES, verbose_name="Tipo de evento")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data do evento")
    payload = models.JSONField(verbose_name="Dados")
    tenant_id = models.CharField(max_length=50, verbose_name="ID do tenant")

    def __str__(self):
        return f"{self.type} at {self.created_at}"

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ["-created_at"]
