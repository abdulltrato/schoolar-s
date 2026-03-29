from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseCodeModel, tenant_id_from_user

from .classroom import Classroom
from .school import School


class Announcement(BaseCodeModel):
    CODE_PREFIX = "ANN"
    TENANT_INHERIT_USER_FIELDS = ("author",)
    REQUEST_USER_CREATE_FIELDS = ("author",)
    AUDIENCE_CHOICES = [
        ("school", "Escola"),
        ("classroom", "Turma"),
        ("teachers", "Professores"),
        ("guardians", "Encarregados"),
        ("students", "Alunos"),
    ]

    school = models.ForeignKey(School, on_delete=models.CASCADE, verbose_name="Escola")
    classroom = models.ForeignKey(Classroom, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Turma")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False,
        verbose_name="Autor",
    )
    title = models.CharField(max_length=180, verbose_name="Título")
    message = models.TextField(verbose_name="Mensagem")
    audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, verbose_name="Audiência")
    published_at = models.DateTimeField(auto_now_add=True, verbose_name="Publicado em")
    active = models.BooleanField(default=True, verbose_name="Ativo")

    def clean(self):
        classroom_tenant = (self.classroom.tenant_id or "").strip() if self.classroom_id else ""
        school_tenant = (self.school.tenant_id or "").strip() if self.school_id else ""
        author_tenant = tenant_id_from_user(self.author)
        if self.tenant_id and classroom_tenant and self.tenant_id != classroom_tenant:
            raise ValidationError({"tenant_id": "O tenant do comunicado deve coincidir com o tenant da turma."})
        if self.tenant_id and school_tenant and self.tenant_id != school_tenant:
            raise ValidationError({"tenant_id": "O tenant do comunicado deve coincidir com o tenant da escola."})
        if self.tenant_id and author_tenant and self.tenant_id != author_tenant:
            raise ValidationError({"tenant_id": "O tenant do comunicado deve coincidir com o tenant do autor."})
        if classroom_tenant and author_tenant and classroom_tenant != author_tenant:
            raise ValidationError({"tenant_id": "Turma e autor devem pertencer ao mesmo tenant."})
        if school_tenant and classroom_tenant and school_tenant != classroom_tenant:
            raise ValidationError({"tenant_id": "Escola e turma devem pertencer ao mesmo tenant."})
        if school_tenant and author_tenant and school_tenant != author_tenant:
            raise ValidationError({"tenant_id": "Escola e autor devem pertencer ao mesmo tenant."})
        self.tenant_id = self.tenant_id or classroom_tenant or author_tenant or school_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id é obrigatório."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Comunicado"
        verbose_name_plural = "Comunicados"
        ordering = ["-published_at"]
