import re

from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseCodeModel


def validate_academic_year_code(code: str) -> str:
    """
    Accepts codes in the form YYYY-YYYY (or YYYY/YYYY) where the second year is the first + 1.
    Returns the normalized code using a hyphen.
    If code is falsy, caller should build it from the dates.
    """
    if not code:
        return code

    normalized = code.strip().replace("/", "-")
    if not re.fullmatch(r"\d{4}-\d{4}", normalized):
        raise ValidationError("Use o formato YYYY-YYYY.")

    start_year, end_year = [int(value) for value in normalized.split("-")]
    # Permit same-year spans (calendário) and consecutive-year spans (lectivo)
    if end_year < start_year:
        raise ValidationError("O ano letivo deve terminar no mesmo ano ou no ano seguinte ao de início.")
    return normalized


class AcademicYear(BaseCodeModel):
    CODE_PREFIX = "ACY"
    AUTO_CODE = False

    code = models.CharField(max_length=9, verbose_name="Ano letivo")
    start_date = models.DateField(verbose_name="Data de início")
    end_date = models.DateField(verbose_name="Data de fim")
    active = models.BooleanField(default=False, verbose_name="Ativo")

    def clean(self):
        self.tenant_id = (self.tenant_id or "").strip()
        if not self.tenant_id:
            raise ValidationError({"tenant_id": "tenant_id é obrigatório."})

        provided_code = (self.code or "").strip()
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValidationError({"end_date": "A data de fim não pode ser anterior à data de início."})
            if not provided_code:
                provided_code = f"{self.start_date.year}-{self.end_date.year}"

        self.code = validate_academic_year_code(provided_code)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = "Ano letivo"
        verbose_name_plural = "Anos letivos"
        ordering = ["-code"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "code"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_academic_year_code_active",
            ),
        ]
