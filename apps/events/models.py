from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseCodeModel


class Event(BaseCodeModel):
    TYPE_CHOICES = [
        ("student_registered", "Aluno registado"),
        ("assessment_recorded", "Avaliação registada"),
        ("competency_updated", "Competência atualizada"),
        ("cycle_completed", "Ciclo concluído"),
        ("report_generated", "Relatório gerado"),
    ]
    LEGACY_TYPE_MAP = {
        "aluno_registrado": "student_registered",
        "avaliacao_registada": "assessment_recorded",
        "competencia_atualizada": "competency_updated",
        "ciclo_concluido": "cycle_completed",
        "relatorio_gerado": "report_generated",
    }

    def __init__(self, *args, **kwargs):
        legacy_type = kwargs.pop("tipo", None)
        legacy_payload = kwargs.pop("dados", None)
        if legacy_type is not None and "type" not in kwargs:
            kwargs["type"] = legacy_type
        if legacy_payload is not None and "payload" not in kwargs:
            kwargs["payload"] = legacy_payload
        normalized_type = kwargs.get("type")
        if normalized_type is not None:
            kwargs["type"] = self.LEGACY_TYPE_MAP.get(normalized_type, normalized_type)
        super().__init__(*args, **kwargs)

    def clean(self):
        self.type = self.LEGACY_TYPE_MAP.get(self.type, self.type)
        self.tenant_id = (self.tenant_id or "").strip()
        if not self.tenant_id:
            raise ValidationError({"tenant_id": "tenant_id is required."})

    def save(self, *args, **kwargs):
        self.type = self.LEGACY_TYPE_MAP.get(self.type, self.type)
        self.full_clean()
        return super().save(*args, **kwargs)

    type = models.CharField(max_length=50, choices=TYPE_CHOICES, verbose_name="Tipo de evento")
    payload = models.JSONField(verbose_name="Dados")

    def __str__(self):
        return f"{self.type} at {self.created_at}"

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ["-created_at"]
