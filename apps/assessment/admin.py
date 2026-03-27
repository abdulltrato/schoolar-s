from django.contrib import admin

from core.admin_utils import TenantAwareAdmin

from .models import (
    AssessmentPeriod,
    AssessmentComponent,
    AssessmentOutcomeMap,
    Assessment,
    SubjectPeriodResult,
)


@admin.register(AssessmentPeriod)
class AssessmentPeriodAdmin(TenantAwareAdmin):
    pass


@admin.register(AssessmentComponent)
class AssessmentComponentAdmin(TenantAwareAdmin):
    pass


@admin.register(AssessmentOutcomeMap)
class AssessmentOutcomeMapAdmin(TenantAwareAdmin):
    pass


@admin.register(Assessment)
class AssessmentAdmin(TenantAwareAdmin):
    pass


@admin.register(SubjectPeriodResult)
class SubjectPeriodResultAdmin(TenantAwareAdmin):
    pass
