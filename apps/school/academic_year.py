from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseCodeModel


class AcademicYear(BaseCodeModel):
    CODE_PREFIX = "ACY"

    start_date = models.DateField(verbose_name="Data de início")
    end_date = models.DateField(verbose_name="Data de fim")
    active = models.BooleanField(default=True, verbose_name="Ativo")

    def clean(self):
        if self.end_date and self.start_date and self.end_date <= self.start_date:
            raise ValidationError({"end_date": "A data de fim deve ser posterior à data de início."})

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = "Ano letivo"
        verbose_name_plural = "Anos letivos"
        ordering = ["-code"]
