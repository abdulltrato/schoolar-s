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
    pass


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
    pass


@admin.register(CompetencyOutcome)
class CompetencyOutcomeAdmin(DerivedTenantAdmin):
    pass


@admin.register(SubjectCurriculumPlan)
class SubjectCurriculumPlanAdmin(DerivedTenantAdmin):
    pass
