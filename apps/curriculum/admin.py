from django.contrib import admin
# Ferramentas de registro do Django admin.

from core.admin_utils import DerivedTenantAdmin, TenantAwareAdmin
# Mixins utilitários para lidar com tenant e derivação de tenant.

from .models import (
    CurriculumArea,
    Subject,
    SubjectSpecialty,
    Competency,
    LearningOutcome,
    CompetencyOutcome,
    BaseCurriculum,
    LocalCurriculum,
    SubjectCurriculumPlan,
)
# Modelos do domínio de currículo usados no admin.


@admin.register(CurriculumArea)
class CurriculumAreaAdmin(TenantAwareAdmin):
    """Administra áreas curriculares com filtro por tenant."""

    # Colunas exibidas na listagem.
    list_display = ("name", "tenant_id")


@admin.register(BaseCurriculum)
class BaseCurriculumAdmin(TenantAwareAdmin):
    """Admin básico para currículos-base."""
    # Nenhuma customização adicional além do mixin de tenant.
    pass


@admin.register(LocalCurriculum)
class LocalCurriculumAdmin(TenantAwareAdmin):
    """Admin para currículos locais (variações por tenant)."""
    # Usa comportamento padrão do mixin.
    pass


@admin.register(LearningOutcome)
class LearningOutcomeAdmin(TenantAwareAdmin):
    """Administra resultados de aprendizagem ligados a competências."""
    # Configuração padrão; poderia receber filtros no futuro.
    pass


@admin.register(Subject)
class SubjectAdmin(DerivedTenantAdmin):
    """Admin para disciplinas, com pesquisa por nome, código e tenant."""

    # Campos permitidos na busca textual do admin.
    search_fields = ("name", "code", "tenant_id")


@admin.register(SubjectSpecialty)
class SubjectSpecialtyAdmin(DerivedTenantAdmin):
    """Administra especialidades vinculadas a disciplinas."""

    # Mostra disciplina e dados de deleção para controle.
    list_display = ("name", "subject", "tenant_id", "deleted_at")


@admin.register(Competency)
class CompetencyAdmin(DerivedTenantAdmin):
    """Admin para competências, exibindo contexto de área, disciplina e ciclo."""

    # Colunas principais, incluindo nome amigável do tenant.
    list_display = ("name", "code", "tenant_name", "area", "subject", "grade", "cycle", "deleted_at")

    def tenant_name(self, obj):
        """Resolve nome do tenant a partir de School ou mostra o ID cru."""
        from apps.school.models import School

        # Busca nome da escola para o tenant; fallback para ID.
        name = School.objects.filter(tenant_id=obj.tenant_id).values_list("name", flat=True).first()
        return name or obj.tenant_id

    # Configurações de exibição e ordenação do método acima.
    tenant_name.short_description = "Tenant"
    tenant_name.admin_order_field = "tenant_id"


@admin.register(CompetencyOutcome)
class CompetencyOutcomeAdmin(DerivedTenantAdmin):
    """Admin para alinhamentos entre competência e resultado."""
    # Sem personalização específica.
    pass


@admin.register(SubjectCurriculumPlan)
class SubjectCurriculumPlanAdmin(DerivedTenantAdmin):
    """Admin para planos curriculares por disciplina."""
    # Configuração padrão com suporte a tenant.
    pass
