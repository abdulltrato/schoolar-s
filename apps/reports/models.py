from django.core.exceptions import ValidationError
from django.db import models


class Report(models.Model):
    TYPE_CHOICES = [
        ("student", "Relatório do aluno"),
        ("school", "Relatório da escola"),
        ("national", "Relatório nacional"),
    ]

    title = models.CharField(max_length=200, verbose_name="Título")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Tipo")
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de geração")
    period = models.CharField(max_length=50, blank=True, verbose_name="Período")
    content = models.JSONField(verbose_name="Conteúdo")
    student = models.ForeignKey("academic.Student", on_delete=models.CASCADE, null=True, blank=True, verbose_name="Aluno")

    def clean(self):
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
