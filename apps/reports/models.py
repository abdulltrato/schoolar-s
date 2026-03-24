import hashlib
import hmac
import json
import secrets

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from core.models import BaseCodeModel


class Report(BaseCodeModel):
    TYPE_CHOICES = [
        ("student", "Relatório do aluno"),
        ("school", "Relatório da escola"),
        ("national", "Relatório nacional"),
    ]
    LEGACY_TYPE_MAP = {
        "aluno": "student",
        "escola": "school",
        "nacional": "national",
    }

    def __init__(self, *args, **kwargs):
        legacy_title = kwargs.pop("titulo", None)
        legacy_type = kwargs.pop("tipo", None)
        legacy_content = kwargs.pop("conteudo", None)
        if legacy_title is not None and "title" not in kwargs:
            kwargs["title"] = legacy_title
        if legacy_type is not None and "type" not in kwargs:
            kwargs["type"] = legacy_type
        if legacy_content is not None and "content" not in kwargs:
            kwargs["content"] = legacy_content
        super().__init__(*args, **kwargs)

    title = models.CharField(max_length=200, verbose_name="Título")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Tipo")
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de geração")
    period = models.CharField(max_length=50, blank=True, verbose_name="Período")
    content = models.JSONField(verbose_name="Conteúdo")
    student = models.ForeignKey("academic.Student", on_delete=models.CASCADE, null=True, blank=True, verbose_name="Aluno")
    serial_number = models.CharField(max_length=40, unique=True, blank=True, editable=False, verbose_name="Número de série")
    verification_code = models.CharField(max_length=32, unique=True, blank=True, editable=False, verbose_name="Código de verificação")
    verification_hash = models.CharField(max_length=64, blank=True, editable=False, verbose_name="Assinatura de verificação")
    verification_version = models.PositiveSmallIntegerField(default=1, editable=False, verbose_name="Versão de verificação")

    def clean(self):
        self.type = self.LEGACY_TYPE_MAP.get(self.type, self.type)
        if self.type == "student" and not self.student_id:
            raise ValidationError({"student": "Student reports require an associated student."})
        if self.type != "student" and self.student_id:
            raise ValidationError({"student": "Only student reports may reference a student."})
        student_tenant = (self.student.tenant_id or "").strip() if self.student_id else ""
        if student_tenant:
            if self.tenant_id and self.tenant_id != student_tenant:
                raise ValidationError({"tenant_id": "Report tenant must match the student tenant."})
            if not self.tenant_id:
                self.tenant_id = student_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id is required."})

    def _build_verification_payload(self):
        content = self.content if isinstance(self.content, dict) else {}
        payload = {
            "id": self.pk,
            "title": self.title,
            "type": self.type,
            "period": self.period,
            "student_id": self.student_id,
            "generated_at": self.generated_at.isoformat() if self.generated_at else "",
            "verification_code": self.verification_code,
            "verification_version": self.verification_version,
            "content": content,
        }
        return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)

    def calculate_verification_hash(self):
        payload = self._build_verification_payload().encode("utf-8")
        return hmac.new(settings.SECRET_KEY.encode("utf-8"), payload, hashlib.sha256).hexdigest()

    def verify_integrity(self, provided_hash=None):
        expected_hash = self.calculate_verification_hash()
        stored_matches = hmac.compare_digest(self.verification_hash or "", expected_hash)
        if provided_hash is None:
            return stored_matches
        return stored_matches and hmac.compare_digest(provided_hash, self.verification_hash or "")

    def _generate_verification_code(self):
        return f"RPT-{secrets.token_hex(6).upper()}"

    def _series_prefix(self):
        if self.type == "student":
            return "ALN"
        if self.type == "school":
            return "ESC"
        return "NAC"

    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.verification_code:
            self.verification_code = self._generate_verification_code()

        result = super().save(*args, **kwargs)
        if not self.serial_number:
            year_label = (self.generated_at.year if self.generated_at else timezone.now().year)
            self.serial_number = f"{self._series_prefix()}-{year_label}-{self.pk:06d}"
            type(self).objects.filter(pk=self.pk).update(serial_number=self.serial_number)
        verification_hash = self.calculate_verification_hash()
        if self.verification_hash != verification_hash:
            self.verification_hash = verification_hash
            type(self).objects.filter(pk=self.pk).update(verification_hash=verification_hash)
        return result

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Relatório"
        verbose_name_plural = "Relatórios"
        ordering = ["-generated_at"]
