from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseCodeModel
from core.tenant_mixins import TenantValidationMixin
from .models_courses import CourseOffering
from .validators import validate_lesson_conflicts


class Lesson(BaseCodeModel, TenantValidationMixin):
    CODE_PREFIX = "LES"
    offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, related_name="lessons", verbose_name="Oferta")
    title = models.CharField(max_length=180, verbose_name="Título")
    description = models.TextField(blank=True, verbose_name="Descrição")
    scheduled_at = models.DateTimeField(verbose_name="Agendada para")
    duration_minutes = models.PositiveIntegerField(default=45, verbose_name="Duração em minutos")
    meeting_url = models.URLField(blank=True, verbose_name="Link da aula")
    recording_url = models.URLField(blank=True, verbose_name="Link da gravação")
    published = models.BooleanField(default=False, verbose_name="Publicada")

    def clean(self):
        offering_tenant = (self.offering.tenant_id or "").strip() if self.offering_id else ""
        if self.tenant_id and offering_tenant and self.tenant_id != offering_tenant:
            raise ValidationError({"tenant_id": "O tenant da aula deve coincidir com o tenant da oferta."})
        self.ensure_tenant(offering_tenant, self.tenant_id)
        validate_lesson_conflicts(self)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Aula"
        verbose_name_plural = "Aulas"
        ordering = ["scheduled_at"]


class LessonMaterial(BaseCodeModel):
    CODE_PREFIX = "LMT"
    TYPE_CHOICES = [
        ("link", "Link"),
        ("document", "Documento"),
        ("video", "Vídeo"),
        ("audio", "Áudio"),
        ("other", "Outro"),
    ]

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="materials", verbose_name="Aula")
    title = models.CharField(max_length=180, verbose_name="Título")
    material_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Tipo")
    # Campos individuais por tipo, habilitados por checkbox
    link_enabled = models.BooleanField(default=False, verbose_name="Usar link")
    link_url = models.URLField(blank=True, verbose_name="Link")

    video_enabled = models.BooleanField(default=False, verbose_name="Usar vídeo")
    video_url = models.URLField(blank=True, verbose_name="URL do vídeo")

    audio_enabled = models.BooleanField(default=False, verbose_name="Usar áudio")
    audio_url = models.URLField(blank=True, verbose_name="URL do áudio")

    document_enabled = models.BooleanField(default=False, verbose_name="Usar documento (PDF/Word)")
    document_file = models.FileField(upload_to="lesson_materials/docs/", blank=True, null=True, verbose_name="Documento")

    image_enabled = models.BooleanField(default=False, verbose_name="Usar imagem")
    image_file = models.ImageField(upload_to="lesson_materials/images/", blank=True, null=True, verbose_name="Imagem")

    required = models.BooleanField(default=False, verbose_name="Obrigatório")

    def clean(self):
        lesson_tenant = (self.lesson.tenant_id or "").strip() if self.lesson_id else ""
        if lesson_tenant:
            if self.tenant_id and self.tenant_id != lesson_tenant:
                raise ValidationError({"tenant_id": "O tenant do material deve coincidir com o tenant da aula."})
            if not self.tenant_id:
                self.tenant_id = lesson_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id é obrigatório. Envie o header X-Tenant-ID ou configure tenant_id no seu perfil (UserProfile)."})

        # Pelo menos um canal deve estar habilitado
        channels_enabled = [
            self.link_enabled,
            self.video_enabled,
            self.audio_enabled,
            self.document_enabled,
            self.image_enabled,
        ]
        if not any(channels_enabled):
            raise ValidationError({"material_type": "Selecione pelo menos um tipo de recurso (link, vídeo, áudio, documento ou imagem)."})

        errors = {}
        if self.link_enabled and not (self.link_url or "").strip():
            errors["link_url"] = "Informe o link."
        if self.video_enabled and not (self.video_url or "").strip():
            errors["video_url"] = "Informe a URL do vídeo."
        if self.audio_enabled and not (self.audio_url or "").strip():
            errors["audio_url"] = "Informe a URL do áudio."
        if self.document_enabled and not self.document_file:
            errors["document_file"] = "Envie o documento (PDF/Word)."
        if self.image_enabled and not self.image_file:
            errors["image_file"] = "Envie a imagem."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Material da aula"
        verbose_name_plural = "Materiais da aula"
        ordering = ["lesson__scheduled_at", "title"]
