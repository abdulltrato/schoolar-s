from apps.assessment.models import (
    Assessment,
    AssessmentComponent,
    AssessmentOutcomeMap,
    AssessmentPeriod,
    SubjectPeriodResult,
)


def backfill_assessment_entities(runner):
    runner._backfill_queryset(
        label="AssessmentPeriod",
        queryset=AssessmentPeriod.objects.select_related("academic_year"),
        candidate_fn=lambda obj: [
            getattr(obj.academic_year, "tenant_id", ""),
        ],
        model=AssessmentPeriod,
    )

    runner._backfill_queryset(
        label="AssessmentComponent",
        queryset=AssessmentComponent.objects.select_related("period", "grade_subject"),
        candidate_fn=lambda obj: [
            getattr(obj.period, "tenant_id", ""),
            getattr(obj.grade_subject, "tenant_id", ""),
        ],
        model=AssessmentComponent,
    )

    runner._backfill_queryset(
        label="AssessmentOutcomeMap",
        queryset=AssessmentOutcomeMap.objects.select_related("component", "outcome"),
        candidate_fn=lambda obj: [
            getattr(obj.component, "tenant_id", ""),
            getattr(obj.outcome, "tenant_id", ""),
        ],
        model=AssessmentOutcomeMap,
    )

    runner._backfill_queryset(
        label="Assessment",
        queryset=Assessment.objects.select_related("student", "teaching_assignment", "period", "component", "competency"),
        candidate_fn=lambda obj: [
            getattr(obj.student, "tenant_id", ""),
            getattr(obj.teaching_assignment, "tenant_id", ""),
            getattr(obj.period, "tenant_id", ""),
            getattr(obj.component, "tenant_id", ""),
            getattr(obj.competency, "tenant_id", ""),
        ],
        model=Assessment,
    )

    runner._backfill_queryset(
        label="SubjectPeriodResult",
        queryset=SubjectPeriodResult.objects.select_related("student", "teaching_assignment", "period"),
        candidate_fn=lambda obj: [
            getattr(obj.student, "tenant_id", ""),
            getattr(obj.teaching_assignment, "tenant_id", ""),
            getattr(obj.period, "tenant_id", ""),
        ],
        model=SubjectPeriodResult,
    )
