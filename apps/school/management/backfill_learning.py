from apps.learning.models import Assignment, Course, CourseOffering, Lesson, Submission


def backfill_learning_entities(runner):
    runner._backfill_queryset(
        label="Course",
        queryset=Course.objects.select_related("school"),
        candidate_fn=lambda obj: [
            getattr(obj.school, "tenant_id", ""),
        ],
        model=Course,
    )

    runner._backfill_queryset(
        label="CourseOffering",
        queryset=CourseOffering.objects.select_related("course", "classroom", "teacher", "academic_year"),
        candidate_fn=lambda obj: [
            getattr(obj.course, "tenant_id", ""),
            getattr(obj.classroom, "tenant_id", ""),
            getattr(obj.teacher, "tenant_id", ""),
            getattr(obj.academic_year, "tenant_id", ""),
        ],
        model=CourseOffering,
    )

    runner._backfill_queryset(
        label="Lesson",
        queryset=Lesson.objects.select_related("offering"),
        candidate_fn=lambda obj: [
            getattr(obj.offering, "tenant_id", ""),
        ],
        model=Lesson,
    )

    runner._backfill_queryset(
        label="Assignment",
        queryset=Assignment.objects.select_related("offering"),
        candidate_fn=lambda obj: [
            getattr(obj.offering, "tenant_id", ""),
        ],
        model=Assignment,
    )

    runner._backfill_queryset(
        label="Submission",
        queryset=Submission.objects.select_related("assignment", "student"),
        candidate_fn=lambda obj: [
            getattr(obj.assignment, "tenant_id", ""),
            getattr(obj.student, "tenant_id", ""),
        ],
        model=Submission,
    )
