from django.contrib import admin
# Importa ferramentas de registro do Django admin.

from core.admin_utils import TenantAwareAdmin
# Admin base que filtra por tenant.

from .assessment import Assessment
# Modelo principal de avaliação.
from .component import AssessmentComponent
# Modelo de componente avaliativo.
from .question import AssessmentQuestion, Question
# Modelos de perguntas e vínculo pergunta-avaliação.
from .period import AssessmentPeriod
# Modelo de período avaliativo.
from .outcome_map import AssessmentOutcomeMap
# Modelo de mapeamento componente-resultado.
from .subject_period_result import SubjectPeriodResult
# Modelo de resultado agregado.


@admin.register(AssessmentPeriod)
class AssessmentPeriodAdmin(TenantAwareAdmin):
    """Admin para períodos avaliativos, herdando filtros por tenant."""

    # Configurações adicionais não necessárias no momento.
    pass


@admin.register(AssessmentComponent)
class AssessmentComponentAdmin(TenantAwareAdmin):
    """Admin para componentes avaliativos."""

    # Configurações extras podem ser adicionadas depois.
    pass


@admin.register(AssessmentOutcomeMap)
class AssessmentOutcomeMapAdmin(TenantAwareAdmin):
    """Admin para mapeamentos de componente para resultado."""

    # Usa comportamento padrão do TenantAwareAdmin.
    pass


class AssessmentQuestionInline(admin.TabularInline):
    """Inline que permite gerenciar perguntas ligadas a avaliações."""

    # Modelo de relação avaliação-pergunta.
    model = AssessmentQuestion
    # Não adiciona formulários extras por padrão.
    extra = 0
    # Usa campo raw_id para buscar perguntas.
    raw_id_fields = ("question",)
    # Rótulos no admin.
    verbose_name = "Pergunta vinculada"
    verbose_name_plural = "Perguntas vinculadas"


@admin.register(Assessment)
class AssessmentAdmin(TenantAwareAdmin):
    """Admin de avaliações, exibindo perguntas vinculadas inline."""

    # Inclui inline de perguntas.
    inlines = [AssessmentQuestionInline]
    # Colunas principais na listagem.
    list_display = ("student", "teaching_assignment", "component", "date")
    pass


@admin.register(SubjectPeriodResult)
class SubjectPeriodResultAdmin(TenantAwareAdmin):
    """Admin para resultados agregados por período/disciplina."""

    # Configuração padrão é suficiente.
    pass


@admin.register(Question)
class QuestionAdmin(TenantAwareAdmin):
    """Admin para perguntas, com filtros e busca."""

    # Colunas exibidas.
    list_display = ("subject", "question_type", "text", "vocational")
    # Campos incluídos na busca.
    search_fields = ("text", "subject__name")
    # Filtros laterais.
    list_filter = ("question_type", "vocational")


@admin.register(AssessmentQuestion)
class AssessmentQuestionAdmin(TenantAwareAdmin):
    """Admin para vínculos de perguntas às avaliações."""

    # Colunas exibidas.
    list_display = ("assessment", "question", "order")
    # Usa raw_id para facilitar seleção de perguntas.
    raw_id_fields = ("question",)
