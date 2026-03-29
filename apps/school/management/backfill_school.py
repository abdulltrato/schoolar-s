from apps.school.models import AcademicYear, Classroom, GradeSubject, School, Teacher, TeachingAssignment, UserProfile


def backfill_school_entities(runner):
    runner._backfill_queryset(
        label="School",
        queryset=School.objects.all(),
        candidate_fn=lambda obj: [obj.tenant_id],
        model=School,
    )

    runner._backfill_queryset(
        label="AcademicYear",
        queryset=AcademicYear.objects.select_related("school"),
        candidate_fn=lambda obj: [getattr(obj.school, "tenant_id", "")],
        model=AcademicYear,
    )

    runner._backfill_queryset(
        label="GradeSubject",
        queryset=GradeSubject.objects.select_related("academic_year", "grade", "subject"),
        candidate_fn=lambda obj: [
            getattr(obj.academic_year, "tenant_id", ""),
            getattr(obj.grade, "tenant_id", ""),
            getattr(obj.subject, "tenant_id", ""),
        ],
        model=GradeSubject,
    )

    runner._backfill_queryset(
        label="Teacher",
        queryset=Teacher.objects.select_related("school", "specialty"),
        candidate_fn=lambda obj: [
            getattr(obj.school, "tenant_id", ""),
            getattr(obj.specialty, "tenant_id", ""),
        ],
        model=Teacher,
    )

    runner._backfill_queryset(
        label="TeachingAssignment",
        queryset=TeachingAssignment.objects.select_related("teacher", "classroom", "grade_subject"),
        candidate_fn=lambda obj: [
            getattr(obj.teacher, "tenant_id", ""),
            getattr(obj.classroom, "tenant_id", ""),
            getattr(obj.grade_subject, "tenant_id", ""),
        ],
        model=TeachingAssignment,
    )

    runner._backfill_queryset(
        label="Classroom",
        queryset=Classroom.objects.select_related("school", "academic_year", "grade", "lead_teacher"),
        candidate_fn=lambda obj: [
            getattr(obj.school, "tenant_id", ""),
            getattr(obj.academic_year, "tenant_id", ""),
            getattr(obj.grade, "tenant_id", ""),
            getattr(obj.lead_teacher, "tenant_id", ""),
        ],
        model=Classroom,
    )

    runner._backfill_queryset(
        label="UserProfile",
        queryset=UserProfile.objects.select_related("school"),
        candidate_fn=lambda obj: [
            getattr(obj.school, "tenant_id", ""),
            getattr(obj.user, "tenant_id", ""),
        ],
        model=UserProfile,
    )
