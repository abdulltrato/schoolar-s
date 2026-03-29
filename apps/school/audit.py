from django.db import models

from core.models import BaseCodeModel


class AuditEvent(BaseCodeModel):
    CODE_PREFIX = "AUE"

    resource = models.CharField(max_length=200, verbose_name="Recurso")
    action = models.CharField(max_length=50, verbose_name="Ação")
    severity = models.CharField(max_length=20, default="watch", verbose_name="Severidade")
    details = models.JSONField(default=dict, blank=True, verbose_name="Detalhes")
    author = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_events", verbose_name="Autor")

    class Meta:
        verbose_name = "Evento de auditoria"
        verbose_name_plural = "Eventos de auditoria"


class AuditAlert(BaseCodeModel):
    CODE_PREFIX = "AUA"

    resource = models.CharField(max_length=200, verbose_name="Recurso")
    username = models.CharField(max_length=150, blank=True, verbose_name="Utilizador")
    severity = models.CharField(max_length=20, default="watch", verbose_name="Severidade")
    acknowledged = models.BooleanField(default=False, verbose_name="Reconhecido")
    message = models.TextField(blank=True, verbose_name="Mensagem")

    class Meta:
        verbose_name = "Alerta de auditoria"
        verbose_name_plural = "Alertas de auditoria"
