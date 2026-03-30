from django.core.exceptions import ValidationError
# Importa exceção para validar regras customizadas.
from django.db import models
# Importa ORM do Django.

from core.models import BaseNamedCodeModel
# Modelo base com nome e código gerado.
from .period import AssessmentPeriod
# Período avaliativo usado na FK.


class AssessmentComponent(BaseNamedCodeModel):
    """Configura um componente avaliativo (teste, exame, trabalho) para uma disciplina em um período."""

    # Prefixo usado na geração de códigos automáticos.
    CODE_PREFIX = "CMP"
    # Lista de tipos disponíveis para componentes.
    TYPE_CHOICES = [
        ("acs", "ACS"),
        ("acp", "ACP"),
        ("individual_work", "Trabalho individual"),
        ("group_work", "Trabalho em grupo"),
        ("test", "Teste"),
        ("exam", "Exame"),
        ("diagnostic", "Diagnóstica"),
        ("formative", "Formativa"),
        ("summative", "Summativa"),
        ("other", "Outra"),
    ]
    # Mapa de valores legados para novos valores de tipo.
    LEGACY_TYPE_MAP = {
        "teste": "test",
        "exame": "exam",
        "diagnostica": "diagnostic",
        "formativa": "formative",
        "sumativa": "summative",
        "outra": "other",
    }

    def __init__(self, *args, **kwargs):
        # Aceita campo legado `tipo` e converte para `type` se necessário.
        legacy_type = kwargs.pop("tipo", None)
        if legacy_type is not None and "type" not in kwargs:
            kwargs["type"] = legacy_type
        # Normaliza valor do tipo, convertendo alias legados.
        normalized_type = kwargs.get("type")
        if normalized_type is not None:
            kwargs["type"] = self.LEGACY_TYPE_MAP.get(normalized_type, normalized_type)
        # Continua a inicialização padrão.
        super().__init__(*args, **kwargs)

    # Período avaliativo ao qual este componente pertence.
    period = models.ForeignKey(AssessmentPeriod, on_delete=models.CASCADE, verbose_name="Período")
    # Disciplina da classe vinculada ao componente.
    grade_subject = models.ForeignKey("school.GradeSubject", on_delete=models.CASCADE, verbose_name="Disciplina da classe")
    # Tipo do componente (teste, exame, etc.).
    type = models.CharField(max_length=30, choices=TYPE_CHOICES, verbose_name="Tipo")
    # Peso percentual usado no cálculo da média.
    weight = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Peso")
    # Nota máxima possível.
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=20, verbose_name="Nota máxima")
    # Indica se o componente é obrigatório.
    mandatory = models.BooleanField(default=True, verbose_name="Obrigatória")

    def clean(self):
        # Normaliza tipos legados.
        self.type = self.LEGACY_TYPE_MAP.get(self.type, self.type)
        # Garante que período e disciplina estejam no mesmo ano letivo.
        if self.period.academic_year_id != self.grade_subject.academic_year_id:
            raise ValidationError({"grade_subject": "The grade subject must belong to the same academic year as the period."})
        # Captura tenants para validação cruzada.
        period_tenant = (self.period.tenant_id or "").strip() if self.period_id else ""
        grade_subject_tenant = (self.grade_subject.tenant_id or "").strip() if self.grade_subject_id else ""
        # Confere consistência entre período e disciplina.
        if period_tenant and grade_subject_tenant and period_tenant != grade_subject_tenant:
            raise ValidationError({"tenant_id": "Assessment component tenant must match across period and grade subject."})
        # Confere consistência com tenant explícito.
        if self.tenant_id and period_tenant and self.tenant_id != period_tenant:
            raise ValidationError({"tenant_id": "Assessment component tenant must match the period tenant."})
        if self.tenant_id and grade_subject_tenant and self.tenant_id != grade_subject_tenant:
            raise ValidationError({"tenant_id": "Assessment component tenant must match the grade subject tenant."})
        # Preenche tenant herdado quando vazio.
        self.tenant_id = self.tenant_id or period_tenant or grade_subject_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id is required."})
        # Impede peso fora do intervalo 0-100.
        if self.weight <= 0 or self.weight > 100:
            raise ValidationError({"weight": "Weight must be between 0 and 100."})
        # Nota máxima precisa ser positiva.
        if self.max_score <= 0:
            raise ValidationError({"max_score": "Maximum score must be positive."})

    def save(self, *args, **kwargs):
        # Normaliza tipo antes de salvar.
        self.type = self.LEGACY_TYPE_MAP.get(self.type, self.type)
        # Executa validações de domínio.
        self.full_clean()
        # Persiste registro.
        return super().save(*args, **kwargs)

    def __str__(self):
        # Exibe nome e disciplina para identificar o componente.
        return f"{self.name} - {self.grade_subject.subject}"

    class Meta:
        # Rótulos no admin.
        verbose_name = "Componente avaliativa"
        verbose_name_plural = "Componentes avaliativas"
        # Ordenação padrão.
        ordering = ["period__academic_year__code", "period__order", "grade_subject__subject__name", "name"]
        # Garante unicidade de nome por período e disciplina enquanto ativo.
        constraints = [
            models.UniqueConstraint(
                fields=["period", "grade_subject", "name"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_assessment_component_active",
            ),
        ]
