import re
# Regex para validar formato do código do ano letivo.

from django.core.exceptions import ValidationError
# Exceção de validação de domínio.
from django.db import models
# Campos e utilitários do ORM.

from core.models import BaseCodeModel
# Modelo base com código, auditoria e soft-delete.


def validate_academic_year_code(code: str) -> str:
    """
    Valida códigos no formato YYYY-YYYY (ou YYYY/YYYY) permitindo ano igual ou consecutivo.

    Retorna o código normalizado com hífen. Se o código for falsy, o caller deve montá-lo
    a partir das datas (start_date/end_date).
    """
    if not code:
        return code

    normalized = code.strip().replace("/", "-")
    if not re.fullmatch(r"\d{4}-\d{4}", normalized):
        raise ValidationError("Use o formato YYYY-YYYY.")

    start_year, end_year = [int(value) for value in normalized.split("-")]
    # Permite períodos dentro do mesmo ano ou ano seguinte.
    if end_year < start_year:
        raise ValidationError("O ano letivo deve terminar no mesmo ano ou no ano seguinte ao de início.")
    return normalized


class AcademicYear(BaseCodeModel):
    """Ano letivo com código validado, datas de início/fim e flag de ativo."""

    CODE_PREFIX = "ACY"
    AUTO_CODE = False

    # Código legível (ex.: 2026-2027).
    code = models.CharField(max_length=9, verbose_name="Ano letivo")
    # Data de início do ano letivo.
    start_date = models.DateField(verbose_name="Data de início")
    # Data de término do ano letivo.
    end_date = models.DateField(verbose_name="Data de fim")
    # Indica se é o ano letivo vigente.
    active = models.BooleanField(default=False, verbose_name="Ativo")

    def clean(self):
        """Normaliza tenant, valida datas e gera código quando ausente."""
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
        """Executa validação completa antes de salvar."""
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        """Retorna o código para exibição."""
        return self.code

    class Meta:
        # Rótulos administrativos.
        verbose_name = "Ano letivo"
        verbose_name_plural = "Anos letivos"
        # Ordena por código desc (mais recente primeiro).
        ordering = ["-code"]
        # Garante unicidade de código por tenant enquanto ativo.
        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "code"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_academic_year_code_active",
            ),
        ]
