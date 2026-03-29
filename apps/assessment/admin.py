from django.contrib import admin

from core.admin_utils import TenantAwareAdmin

from .assessment import Assessment
from .component import AssessmentComponent
from .question import AssessmentQuestion, Question
from .period import AssessmentPeriod
from .outcome_map import AssessmentOutcomeMap
from .subject_period_result import SubjectPeriodResult


@admin.register(AssessmentPeriod)
class AssessmentPeriodAdmin(TenantAwareAdmin):
    pass


@admin.register(AssessmentComponent)
class AssessmentComponentAdmin(TenantAwareAdmin):
    pass


@admin.register(AssessmentOutcomeMap)
class AssessmentOutcomeMapAdmin(TenantAwareAdmin):
    pass


class AssessmentQuestionInline(admin.TabularInline):
    model = AssessmentQuestion
    extra = 0
    raw_id_fields = ("question",)
    verbose_name = "Pergunta vinculada"
    verbose_name_plural = "Perguntas vinculadas"


@admin.register(Assessment)
class AssessmentAdmin(TenantAwareAdmin):
    inlines = [AssessmentQuestionInline]
    list_display = ("student", "teaching_assignment", "component", "date")
    pass


@admin.register(SubjectPeriodResult)
class SubjectPeriodResultAdmin(TenantAwareAdmin):
    pass


@admin.register(Question)
class QuestionAdmin(TenantAwareAdmin):
    list_display = ("subject", "question_type", "text", "vocational")
    search_fields = ("text", "subject__name")
    list_filter = ("question_type", "vocational")


@admin.register(AssessmentQuestion)
class AssessmentQuestionAdmin(TenantAwareAdmin):
    list_display = ("assessment", "question", "order")
    raw_id_fields = ("question",)
