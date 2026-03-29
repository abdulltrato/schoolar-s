from apps.curriculum.models import CompetencyOutcome, LearningOutcome, LocalCurriculum, SubjectCurriculumPlan


def backfill_curriculum_entities(runner):
    runner._backfill_queryset(
        label="LearningOutcome",
        queryset=LearningOutcome.objects.select_related("subject"),
        candidate_fn=lambda obj: [
            getattr(obj.subject, "tenant_id", ""),
        ],
        model=LearningOutcome,
    )

    runner._backfill_queryset(
        label="CompetencyOutcome",
        queryset=CompetencyOutcome.objects.select_related("competency", "outcome"),
        candidate_fn=lambda obj: [
            getattr(obj.competency, "tenant_id", ""),
            getattr(obj.outcome, "tenant_id", ""),
        ],
        model=CompetencyOutcome,
    )

    runner._backfill_queryset(
        label="SubjectCurriculumPlan",
        queryset=SubjectCurriculumPlan.objects.select_related("grade_subject"),
        candidate_fn=lambda obj: [
            getattr(obj.grade_subject, "tenant_id", ""),
        ],
        model=SubjectCurriculumPlan,
    )

    runner._backfill_queryset(
        label="LocalCurriculum",
        queryset=LocalCurriculum.objects.all(),
        candidate_fn=lambda obj: [obj.tenant_id],
        model=LocalCurriculum,
    )
