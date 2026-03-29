from django.db import models

from core.models import BaseCodeModel


class Announcement(BaseCodeModel):
    CODE_PREFIX = "ANN"
    AUDIENCE_CHOICES = [
        ("school", "Escola"),
        ("classroom", "Turma"),
        ("teachers", "Professores"),
        ("guardians", "Encarregados"),
        ("students", "Alunos"),
    ]

    school = models.ForeignKey("school.School", on_delete=models.CASCADE, verbose_name="Escola")
    classroom = models.ForeignKey("school.Classroom", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Turma")
    title = models.CharField(max_length=200, verbose_name="Título")
    message = models.TextField(verbose_name="Mensagem")
    audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default="school", verbose_name="Público")
    active = models.BooleanField(default=True, verbose_name="Ativo")
    author = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="announcements_authored", verbose_name="Autor")

    class Meta:
        verbose_name = "Comunicado"
        verbose_name_plural = "Comunicados"
