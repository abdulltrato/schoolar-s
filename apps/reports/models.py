from django.core.exceptions import ValidationError
from django.db import models


class Report(models.Model):
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

    def clean(self):
        self.type = self.LEGACY_TYPE_MAP.get(self.type, self.type)
        if self.type == "student" and not self.student_id:
            raise ValidationError({"student": "Student reports require an associated student."})
        if self.type != "student" and self.student_id:
            raise ValidationError({"student": "Only student reports may reference a student."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Relatório"
        verbose_name_plural = "Relatórios"
        ordering = ["-generated_at"]
