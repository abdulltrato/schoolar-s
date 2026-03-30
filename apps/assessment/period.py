from django.core.exceptions import ValidationError
# Importa exceção para validar regras de período.
from django.db import models
# Importa tipos de campo do Django.

from core.models import BaseNamedCodeModel
# Modelo base com nome, código e campos auditáveis.


class AssessmentPeriod(BaseNamedCodeModel):
    """Período avaliativo dentro de um ano letivo (ex.: trimestre, semestre)."""

    # Prefixo de código gerado automaticamente.
    CODE_PREFIX = "APR"

    # Ano letivo ao qual o período pertence.
    academic_year = models.ForeignKey("school.AcademicYear", on_delete=models.CASCADE, verbose_name="Ano letivo")
    # Ordem sequencial do período no ano.
    order = models.PositiveSmallIntegerField(verbose_name="Ordem")
    # Data inicial do período avaliativo.
    start_date = models.DateField(verbose_name="Data de início")
    # Data final do período avaliativo.
    end_date = models.DateField(verbose_name="Data de fim")
    # Indica se está ativo.
    active = models.BooleanField(default=True, verbose_name="Ativo")

    def clean(self):
        # Obtém tenant do ano letivo para validar consistência.
        academic_tenant = (self.academic_year.tenant_id or "").strip() if self.academic_year_id else ""
        if academic_tenant:
            # Verifica se tenant informado coincide com o do ano letivo.
            if self.tenant_id and self.tenant_id != academic_tenant:
                raise ValidationError({"tenant_id": "Assessment period tenant must match the academic year tenant."})
            # Herda tenant do ano letivo quando não fornecido.
            if not self.tenant_id:
                self.tenant_id = academic_tenant
        # Exige tenant preenchido.
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id is required."})
        # Garante que a data final seja depois da inicial.
        if self.end_date <= self.start_date:
            raise ValidationError({"end_date": "End date must be later than the start date."})
        # Valida se datas ficam dentro do ano letivo e não sobrepõem outros períodos.
        if self.academic_year_id:
            year = self.academic_year
            # Datas precisam estar contidas no intervalo do ano letivo.
            if self.start_date < year.start_date or self.end_date > year.end_date:
                raise ValidationError({"start_date": "Assessment period must fall within the academic year."})
            # Impede sobreposição com outros períodos do mesmo ano.
            overlapping = AssessmentPeriod.objects.filter(academic_year=year).exclude(pk=self.pk).filter(
                start_date__lte=self.end_date,
                end_date__gte=self.start_date,
            )
            if overlapping.exists():
                raise ValidationError({"start_date": "Assessment period overlaps with an existing period."})

    def save(self, *args, **kwargs):
        # Executa validações antes de salvar.
        self.full_clean()
        # Persiste registro na base.
        return super().save(*args, **kwargs)

    def __str__(self):
        # Exibe nome do período e ano letivo associado.
        return f"{self.name} - {self.academic_year}"

    class Meta:
        # Rótulos no admin.
        verbose_name = "Período avaliativo"
        verbose_name_plural = "Períodos avaliativos"
        # Ordenação padrão.
        ordering = ["academic_year__code", "order"]
        # Garante unicidade de ordem por ano letivo enquanto ativo.
        constraints = [
            models.UniqueConstraint(
                fields=["academic_year", "order"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_assessment_period_order_active",
            ),
        ]
