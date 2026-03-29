from django.contrib import admin

from core.admin_utils import DerivedTenantAdmin, TenantAwareAdmin

from .models import (
    CurriculumArea,
    Subject,
    Competency,
    LearningOutcome,
    CompetencyOutcome,
    BaseCurriculum,
    LocalCurriculum,
    SubjectCurriculumPlan,
)


@admin.register(CurriculumArea)
class CurriculumAreaAdmin(TenantAwareAdmin):
    list_display = ("name", "tenant_id")


@admin.register(BaseCurriculum)
class BaseCurriculumAdmin(TenantAwareAdmin):
    pass


@admin.register(LocalCurriculum)
class LocalCurriculumAdmin(TenantAwareAdmin):
    pass


@admin.register(LearningOutcome)
class LearningOutcomeAdmin(TenantAwareAdmin):
    pass


@admin.register(Subject)
class SubjectAdmin(DerivedTenantAdmin):
    pass


@admin.register(Competency)
class CompetencyAdmin(DerivedTenantAdmin):
    list_display = ("name", "code", "tenant_name", "area", "subject", "grade", "cycle", "deleted_at")

    def tenant_name(self, obj):
        from apps.school.models import School

        name = School.objects.filter(tenant_id=obj.tenant_id).values_list("name", flat=True).first()
        return name or obj.tenant_id

    tenant_name.short_description = "Tenant"
    tenant_name.admin_order_field = "tenant_id"


@admin.register(CompetencyOutcome)
class CompetencyOutcomeAdmin(DerivedTenantAdmin):
    pass


@admin.register(SubjectCurriculumPlan)
class SubjectCurriculumPlanAdmin(DerivedTenantAdmin):
    pass
