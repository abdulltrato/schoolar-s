from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseCodeModel


class AuditEvent(BaseCodeModel):
    CODE_PREFIX = "AUD"
    ACTION_CHOICES = [
        ("create", "Criação"),
        ("update", "Atualização"),
    ]

    resource = models.CharField(max_length=80, verbose_name="Recurso")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="Ação")
    object_id = models.PositiveIntegerField(verbose_name="Identificador do objeto")
    object_repr = models.CharField(max_length=255, blank=True, verbose_name="Representação do objeto")
    request_id = models.CharField(max_length=64, blank=True, verbose_name="Identificador da requisição")
    path = models.CharField(max_length=255, blank=True, verbose_name="Rota")
    method = models.CharField(max_length=10, blank=True, verbose_name="Método")
    role = models.CharField(max_length=40, blank=True, verbose_name="Papel")
    username = models.CharField(max_length=150, blank=True, verbose_name="Nome de utilizador")
    changed_fields = models.JSONField(default=list, blank=True, verbose_name="Campos alterados")

    def clean(self):
        self.tenant_id = (self.tenant_id or "").strip()
        if not self.tenant_id:
            raise ValidationError({"tenant_id": "tenant_id é obrigatório."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.resource}#{self.object_id} {self.action}"

    class Meta:
        verbose_name = "Evento de auditoria"
        verbose_name_plural = "Eventos de auditoria"
        ordering = ["-created_at"]


class AuditAlert(BaseCodeModel):
    CODE_PREFIX = "AAL"
    SEVERITY_CHOICES = [
        ("watch", "Observação"),
        ("elevated", "Elevado"),
    ]

    alert_type = models.CharField(max_length=80, verbose_name="Tipo de alerta")
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, verbose_name="Severidade")
    resource = models.CharField(max_length=80, blank=True, verbose_name="Recurso")
    username = models.CharField(max_length=150, blank=True, verbose_name="Nome de utilizador")
    summary = models.CharField(max_length=255, verbose_name="Resumo")
    details = models.JSONField(default=dict, blank=True, verbose_name="Detalhes")
    acknowledged = models.BooleanField(default=False, verbose_name="Reconhecido")

    def clean(self):
        self.tenant_id = (self.tenant_id or "").strip()
        if not self.tenant_id:
            raise ValidationError({"tenant_id": "tenant_id é obrigatório."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.alert_type} ({self.severity})"

    class Meta:
        verbose_name = "Alerta de auditoria"
        verbose_name_plural = "Alertas de auditoria"
        ordering = ["-created_at"]
