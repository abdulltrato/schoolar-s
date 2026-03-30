from django.core.exceptions import ValidationError
# Exceção de validação.
from django.db import models
# Campos do ORM.

from core.models import BaseCodeModel
# Modelo base com código e auditoria.


class AuditEvent(BaseCodeModel):
    """Evento de auditoria registrando criação/atualização de recursos."""

    CODE_PREFIX = "AUD"
    ACTION_CHOICES = [
        ("create", "Criação"),
        ("update", "Atualização"),
    ]

    # Recurso afetado (ex.: Enrollment).
    resource = models.CharField(max_length=80, verbose_name="Recurso")
    # Ação executada.
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="Ação")
    # Identificador do objeto alvo.
    object_id = models.PositiveIntegerField(verbose_name="Identificador do objeto")
    # Representação textual do objeto.
    object_repr = models.CharField(max_length=255, blank=True, verbose_name="Representação do objeto")
    # Correlação de request para rastreamento.
    request_id = models.CharField(max_length=64, blank=True, verbose_name="Identificador da requisição")
    # Caminho HTTP acessado.
    path = models.CharField(max_length=255, blank=True, verbose_name="Rota")
    # Verbo HTTP.
    method = models.CharField(max_length=10, blank=True, verbose_name="Método")
    # Papel do usuário que executou a ação.
    role = models.CharField(max_length=40, blank=True, verbose_name="Papel")
    # Nome do usuário.
    username = models.CharField(max_length=150, blank=True, verbose_name="Nome de utilizador")
    # Lista de campos alterados.
    changed_fields = models.JSONField(default=list, blank=True, verbose_name="Campos alterados")

    def clean(self):
        """Exige tenant para cada evento."""
        self.tenant_id = (self.tenant_id or "").strip()
        if not self.tenant_id:
            raise ValidationError({"tenant_id": "tenant_id é obrigatório."})

    def save(self, *args, **kwargs):
        """Valida antes de salvar."""
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        """Exibe recurso e ação resumidamente."""
        return f"{self.resource}#{self.object_id} {self.action}"

    class Meta:
        # Rótulos e ordenação mais recentes primeiro.
        verbose_name = "Evento de auditoria"
        verbose_name_plural = "Eventos de auditoria"
        ordering = ["-created_at"]


class AuditAlert(BaseCodeModel):
    """Alerta gerado a partir de eventos de auditoria, com severidade."""

    CODE_PREFIX = "AAL"
    SEVERITY_CHOICES = [
        ("watch", "Observação"),
        ("elevated", "Elevado"),
    ]

    # Tipo/categoria do alerta.
    alert_type = models.CharField(max_length=80, verbose_name="Tipo de alerta")
    # Severidade do evento.
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, verbose_name="Severidade")
    # Recurso relacionado opcional.
    resource = models.CharField(max_length=80, blank=True, verbose_name="Recurso")
    # Usuário relacionado, se aplicável.
    username = models.CharField(max_length=150, blank=True, verbose_name="Nome de utilizador")
    # Resumo curto do alerta.
    summary = models.CharField(max_length=255, verbose_name="Resumo")
    # Dados estruturados adicionais.
    details = models.JSONField(default=dict, blank=True, verbose_name="Detalhes")
    # Indica se alguém reconheceu o alerta.
    acknowledged = models.BooleanField(default=False, verbose_name="Reconhecido")

    def clean(self):
        """Exige tenant para cada alerta."""
        self.tenant_id = (self.tenant_id or "").strip()
        if not self.tenant_id:
            raise ValidationError({"tenant_id": "tenant_id é obrigatório."})

    def save(self, *args, **kwargs):
        """Valida e salva alerta."""
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        """Exibe tipo e severidade."""
        return f"{self.alert_type} ({self.severity})"

    class Meta:
        # Ordena por mais recentes e define rótulos.
        verbose_name = "Alerta de auditoria"
        verbose_name_plural = "Alertas de auditoria"
        ordering = ["-created_at"]
