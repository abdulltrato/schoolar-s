from apps.academic.models import Guardian, Student, StudentCompetency, StudentGuardian, StudentOutcome
from apps.school.models import Enrollment


def backfill_academic_entities(runner):
    runner._backfill_queryset(
        label="Student",
        queryset=Student.objects.select_related("cycle_model", "technical_course"),
        candidate_fn=lambda obj: [
            getattr(obj.cycle_model, "tenant_id", ""),
            getattr(obj.technical_course, "tenant_id", ""),
            obj.tenant_id,
        ],
        model=Student,
    )

    runner._backfill_queryset(
        label="Guardian",
        queryset=Guardian.objects.all(),
        candidate_fn=lambda obj: [obj.tenant_id],
        model=Guardian,
    )

    runner._backfill_queryset(
        label="StudentGuardian",
        queryset=StudentGuardian.objects.select_related("student", "guardian"),
        candidate_fn=lambda obj: [
            getattr(obj.student, "tenant_id", ""),
            getattr(obj.guardian, "tenant_id", ""),
        ],
        model=StudentGuardian,
    )

    runner._backfill_queryset(
        label="StudentCompetency",
        queryset=StudentCompetency.objects.select_related("student", "competency"),
        candidate_fn=lambda obj: [
            getattr(obj.student, "tenant_id", ""),
            getattr(obj.competency, "tenant_id", ""),
        ],
        model=StudentCompetency,
    )

    runner._backfill_queryset(
        label="StudentOutcome",
        queryset=StudentOutcome.objects.select_related("student", "outcome"),
        candidate_fn=lambda obj: [
            getattr(obj.student, "tenant_id", ""),
            getattr(obj.outcome, "tenant_id", ""),
        ],
        model=StudentOutcome,
    )

    runner._backfill_queryset(
        label="Enrollment",
        queryset=Enrollment.objects.select_related("student", "classroom", "classroom__school"),
        candidate_fn=lambda obj: [
            getattr(obj.student, "tenant_id", ""),
            getattr(obj.classroom, "tenant_id", ""),
            getattr(getattr(obj.classroom, "school", None), "tenant_id", ""),
        ],
        model=Enrollment,
    )
