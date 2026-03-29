from django.core.management.base import BaseCommand

from apps.academic.models import Guardian, Student, StudentCompetency, StudentGuardian, StudentOutcome
from apps.assessment.models import (
    Assessment,
    AssessmentComponent,
    AssessmentOutcomeMap,
    AssessmentPeriod,
    SubjectPeriodResult,
)
from apps.curriculum.models import CompetencyOutcome, LearningOutcome, LocalCurriculum, SubjectCurriculumPlan
from apps.events.models import Event
from apps.learning.models import Assignment, Course, CourseOffering, Lesson, Submission
from apps.reports.models import Report
from apps.school.models import (
    AcademicYear,
    Announcement,
    AttendanceRecord,
    AuditAlert,
    AuditEvent,
    Classroom,
    Enrollment,
    GradeSubject,
    Invoice,
    ManagementAssignment,
    Payment,
    School,
    Teacher,
    TeachingAssignment,
    UserProfile,
)
from apps.progress.models import Progression
from .backfill_base import BackfillRunner
from .backfill_school import backfill_school_entities
from .backfill_academic import backfill_academic_entities
from .backfill_assessment import backfill_assessment_entities
from .backfill_curriculum import backfill_curriculum_entities
from .backfill_learning import backfill_learning_entities
from .backfill_finance import backfill_finance_entities
from .backfill_events import backfill_events
from .backfill_audit import backfill_audit


class Command(BaseCommand):
    help = "Backfill tenant_id fields based on related records."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Preview updates without writing changes.")
        parser.add_argument("--strict", action="store_true", help="Fail if any records are missing or conflicting tenant inference.")
        parser.add_argument("--chunk-size", type=int, default=500, help="Batch size for bulk updates.")
        parser.add_argument("--fallback-tenant", default="", help="Tenant id to apply when inference is impossible.")
        parser.add_argument("--max-samples", type=int, default=20, help="Maximum number of conflict/missing samples to print.")

    def handle(self, *args, **options):
        runner = BackfillRunner(
            self.stdout,
            dry_run=options["dry_run"],
            strict=options["strict"],
            chunk_size=max(1, options["chunk_size"]),
            fallback_tenant=options["fallback_tenant"],
            max_samples=max(1, options["max_samples"]),
        )

        def _run():
            backfill_school_entities(runner)
            backfill_academic_entities(runner)
            backfill_assessment_entities(runner)
            backfill_curriculum_entities(runner)
            backfill_learning_entities(runner)
            backfill_finance_entities(runner)
            runner._backfill_queryset(
                label="Progression",
                queryset=Progression.objects.select_related("student", "academic_year"),
                candidate_fn=lambda obj: [
                    getattr(obj.student, "tenant_id", ""),
                    getattr(obj.academic_year, "tenant_id", ""),
                ],
                model=Progression,
            )
            backfill_events(runner)
            backfill_audit(runner)
            runner._backfill_queryset(
                label="Announcement",
                queryset=Announcement.objects.select_related("school", "classroom"),
                candidate_fn=lambda obj: [
                    getattr(obj.school, "tenant_id", ""),
                    getattr(obj.classroom, "tenant_id", ""),
                ],
                model=Announcement,
            )
            runner._backfill_queryset(
                label="AttendanceRecord",
                queryset=AttendanceRecord.objects.select_related("enrollment", "enrollment__student", "enrollment__classroom"),
                candidate_fn=lambda obj: [
                    getattr(obj.enrollment, "tenant_id", ""),
                    getattr(getattr(obj.enrollment, "student", None), "tenant_id", ""),
                    getattr(getattr(obj.enrollment, "classroom", None), "tenant_id", ""),
                ],
                model=AttendanceRecord,
            )
            runner._backfill_queryset(
                label="Report",
                queryset=Report.objects.select_related("student"),
                candidate_fn=lambda obj: [
                    getattr(obj.student, "tenant_id", ""),
                    obj.tenant_id,
                ],
                model=Report,
            )
            runner._backfill_queryset(
                label="Event",
                queryset=Event.objects.all(),
                candidate_fn=lambda obj: [obj.tenant_id],
                model=Event,
            )

        runner.run(_run)
