from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import connection, transaction

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
from apps.progress.models import Progression
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


def _normalize(value):
    return (value or "").strip()


def _pick_tenant(candidates):
    normalized = {value for value in (_normalize(item) for item in candidates) if value}
    if not normalized:
        return None, "missing"
    if len(normalized) > 1:
        return None, "conflict"
    return next(iter(normalized)), None


class Command(BaseCommand):
    help = "Backfill tenant_id fields based on related records."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview updates without writing changes.",
        )
        parser.add_argument(
            "--strict",
            action="store_true",
            help="Fail if any records are missing or conflicting tenant inference.",
        )
        parser.add_argument(
            "--chunk-size",
            type=int,
            default=500,
            help="Batch size for bulk updates.",
        )
        parser.add_argument(
            "--fallback-tenant",
            default="",
            help="Tenant id to apply when inference is impossible.",
        )
        parser.add_argument(
            "--max-samples",
            type=int,
            default=20,
            help="Maximum number of conflict/missing samples to print.",
        )

    def handle(self, *args, **options):
        self.dry_run = options["dry_run"]
        self.strict = options["strict"]
        self.chunk_size = max(1, options["chunk_size"])
        self.fallback_tenant = _normalize(options["fallback_tenant"])
        self.max_samples = max(1, options["max_samples"])

        self.stats = []
        self.samples = []
        self.table_names = set(connection.introspection.table_names())

        with transaction.atomic():
            self._run_backfill()
            if self.dry_run:
                transaction.set_rollback(True)

        self._print_summary()

        if self.strict:
            has_issues = any(entry["missing"] or entry["conflicts"] for entry in self.stats)
            if has_issues:
                raise SystemExit(1)

    def _print_summary(self):
        self.stdout.write("Backfill summary:")
        for entry in self.stats:
            self.stdout.write(
                f"  {entry['label']}: scanned={entry['scanned']} updated={entry['updated']} "
                f"missing={entry['missing']} conflicts={entry['conflicts']}"
            )
        if self.samples:
            self.stdout.write("Samples:")
            for sample in self.samples:
                self.stdout.write(f"  {sample}")
        if self.dry_run:
            self.stdout.write("Dry-run mode enabled: no changes were written.")

    def _record(self, *, label, scanned, updated, missing, conflicts):
        self.stats.append(
            {
                "label": label,
                "scanned": scanned,
                "updated": updated,
                "missing": missing,
                "conflicts": conflicts,
            }
        )

    def _add_sample(self, label, obj_id, detail):
        if len(self.samples) >= self.max_samples:
            return
        self.samples.append(f"{label} id={obj_id}: {detail}")

    def _bulk_update(self, model, rows):
        if not rows:
            return 0
        if not self.dry_run:
            model.objects.bulk_update(rows, ["tenant_id"])
        return len(rows)

    def _backfill_queryset(self, *, label, queryset, candidate_fn, model):
        if not self._table_exists(model):
            self._record(label=label, scanned=0, updated=0, missing=0, conflicts=0)
            self._add_sample(label, "-", f"table {model._meta.db_table} missing")
            return
        scanned = 0
        updated = 0
        missing = 0
        conflicts = 0
        batch = []

        for obj in queryset.iterator():
            scanned += 1
            if _normalize(getattr(obj, "tenant_id", "")):
                continue

            candidates = candidate_fn(obj)
            tenant, status = _pick_tenant(candidates)
            if status == "missing":
                if self.fallback_tenant:
                    tenant = self.fallback_tenant
                    status = None
                else:
                    missing += 1
                    self._add_sample(label, obj.pk, "no tenant candidates")
                    continue
            if status == "conflict":
                conflicts += 1
                self._add_sample(label, obj.pk, f"conflicting tenants={sorted(set(candidates))}")
                continue

            obj.tenant_id = tenant
            batch.append(obj)
            if len(batch) >= self.chunk_size:
                updated += self._bulk_update(model, batch)
                batch = []

        updated += self._bulk_update(model, batch)
        self._record(label=label, scanned=scanned, updated=updated, missing=missing, conflicts=conflicts)

    def _table_exists(self, model):
        return model._meta.db_table in self.table_names

    def _run_backfill(self):
        self._backfill_schools()
        self._backfill_user_profiles()
        self._backfill_teachers()
        self._backfill_students()
        self._backfill_guardians()
        self._backfill_classrooms()
        self._backfill_courses()
        self._backfill_course_offerings()
        self._backfill_management_assignments()
        self._backfill_academic_years()
        self._backfill_grade_subjects()
        self._backfill_teaching_assignments()
        self._backfill_enrollments()
        self._backfill_attendance_records()
        self._backfill_assessment_periods()
        self._backfill_assessment_components()
        self._backfill_assessments()
        self._backfill_subject_period_results()
        self._backfill_curriculum_plans()
        self._backfill_learning_outcomes()
        self._backfill_competency_outcomes()
        self._backfill_lessons()
        self._backfill_assignments()
        self._backfill_submissions()
        self._backfill_reports()
        self._backfill_progressions()
        self._backfill_student_competencies()
        self._backfill_student_guardians()
        self._backfill_student_outcomes()
        self._backfill_invoices()
        self._backfill_payments()
        self._backfill_announcements()
        self._backfill_audit_events()
        self._backfill_audit_alerts()
        self._backfill_local_curricula()
        self._backfill_events()
        self._backfill_assessment_outcome_maps()

    def _backfill_schools(self):
        queryset = School.objects.all()

        def candidates(obj):
            return [obj.code]

        self._backfill_queryset(
            label="School",
            queryset=queryset,
            candidate_fn=candidates,
            model=School,
        )

    def _backfill_user_profiles(self):
        teacher_tenants = dict(Teacher.objects.exclude(tenant_id="").values_list("user_id", "tenant_id"))
        student_tenants = dict(Student.objects.exclude(tenant_id="").values_list("user_id", "tenant_id"))
        guardian_tenants = dict(Guardian.objects.exclude(tenant_id="").values_list("user_id", "tenant_id"))

        queryset = UserProfile.objects.select_related("school", "user")

        def candidates(obj):
            return [
                getattr(obj.school, "tenant_id", ""),
                teacher_tenants.get(obj.user_id, ""),
                student_tenants.get(obj.user_id, ""),
                guardian_tenants.get(obj.user_id, ""),
            ]

        self._backfill_queryset(
            label="UserProfile",
            queryset=queryset,
            candidate_fn=candidates,
            model=UserProfile,
        )

    def _backfill_teachers(self):
        queryset = Teacher.objects.select_related("school", "user__school_profile")

        def candidates(obj):
            return [
                getattr(obj.school, "tenant_id", ""),
                getattr(getattr(obj.user, "school_profile", None), "tenant_id", ""),
            ]

        self._backfill_queryset(
            label="Teacher",
            queryset=queryset,
            candidate_fn=candidates,
            model=Teacher,
        )

    def _backfill_students(self):
        queryset = Student.objects.select_related("user__school_profile")

        def candidates(obj):
            return [
                getattr(getattr(obj.user, "school_profile", None), "tenant_id", ""),
            ]

        self._backfill_queryset(
            label="Student",
            queryset=queryset,
            candidate_fn=candidates,
            model=Student,
        )

    def _backfill_guardians(self):
        queryset = Guardian.objects.select_related("user__school_profile")

        def candidates(obj):
            return [
                getattr(getattr(obj.user, "school_profile", None), "tenant_id", ""),
            ]

        self._backfill_queryset(
            label="Guardian",
            queryset=queryset,
            candidate_fn=candidates,
            model=Guardian,
        )

    def _backfill_classrooms(self):
        queryset = Classroom.objects.select_related("school", "academic_year", "lead_teacher")

        def candidates(obj):
            return [
                getattr(obj.school, "tenant_id", ""),
                getattr(obj.academic_year, "tenant_id", ""),
                getattr(obj.lead_teacher, "tenant_id", ""),
            ]

        self._backfill_queryset(
            label="Classroom",
            queryset=queryset,
            candidate_fn=candidates,
            model=Classroom,
        )

    def _backfill_courses(self):
        queryset = Course.objects.select_related("school")

        def candidates(obj):
            return [getattr(obj.school, "tenant_id", "")]

        self._backfill_queryset(
            label="Course",
            queryset=queryset,
            candidate_fn=candidates,
            model=Course,
        )

    def _backfill_course_offerings(self):
        queryset = CourseOffering.objects.select_related("course", "classroom", "teacher", "academic_year")

        def candidates(obj):
            return [
                getattr(obj.course, "tenant_id", ""),
                getattr(obj.classroom, "tenant_id", ""),
                getattr(obj.teacher, "tenant_id", ""),
                getattr(obj.academic_year, "tenant_id", ""),
            ]

        self._backfill_queryset(
            label="CourseOffering",
            queryset=queryset,
            candidate_fn=candidates,
            model=CourseOffering,
        )

    def _backfill_management_assignments(self):
        queryset = ManagementAssignment.objects.select_related("teacher", "school", "academic_year")

        def candidates(obj):
            return [
                getattr(obj.teacher, "tenant_id", ""),
                getattr(obj.school, "tenant_id", ""),
                getattr(obj.academic_year, "tenant_id", ""),
            ]

        self._backfill_queryset(
            label="ManagementAssignment",
            queryset=queryset,
            candidate_fn=candidates,
            model=ManagementAssignment,
        )

    def _backfill_academic_years(self):
        tenants_by_year = defaultdict(set)
        if self._table_exists(Classroom):
            for ay_id, tenant_id in Classroom.objects.exclude(tenant_id="").values_list("academic_year_id", "tenant_id"):
                if tenant_id:
                    tenants_by_year[ay_id].add(tenant_id)
        if self._table_exists(CourseOffering):
            for ay_id, tenant_id in CourseOffering.objects.exclude(tenant_id="").values_list("academic_year_id", "tenant_id"):
                if tenant_id:
                    tenants_by_year[ay_id].add(tenant_id)
        if self._table_exists(ManagementAssignment):
            for ay_id, tenant_id in ManagementAssignment.objects.exclude(tenant_id="").values_list("academic_year_id", "tenant_id"):
                if tenant_id:
                    tenants_by_year[ay_id].add(tenant_id)
        if self._table_exists(GradeSubject):
            for ay_id, tenant_id in GradeSubject.objects.exclude(tenant_id="").values_list("academic_year_id", "tenant_id"):
                if tenant_id:
                    tenants_by_year[ay_id].add(tenant_id)

        queryset = AcademicYear.objects.all()

        def candidates(obj):
            return list(tenants_by_year.get(obj.pk, set()))

        self._backfill_queryset(
            label="AcademicYear",
            queryset=queryset,
            candidate_fn=candidates,
            model=AcademicYear,
        )

    def _backfill_grade_subjects(self):
        tenants_by_grade_subject = defaultdict(set)
        if self._table_exists(TeachingAssignment):
            for gs_id, tenant_id in TeachingAssignment.objects.exclude(tenant_id="").values_list("grade_subject_id", "tenant_id"):
                if tenant_id:
                    tenants_by_grade_subject[gs_id].add(tenant_id)

        queryset = GradeSubject.objects.select_related("academic_year")

        def candidates(obj):
            return [
                getattr(obj.academic_year, "tenant_id", ""),
                *tenants_by_grade_subject.get(obj.pk, set()),
            ]

        self._backfill_queryset(
            label="GradeSubject",
            queryset=queryset,
            candidate_fn=candidates,
            model=GradeSubject,
        )

    def _backfill_teaching_assignments(self):
        queryset = TeachingAssignment.objects.select_related("teacher", "classroom", "grade_subject")

        def candidates(obj):
            return [
                getattr(obj.teacher, "tenant_id", ""),
                getattr(obj.classroom, "tenant_id", ""),
                getattr(obj.grade_subject, "tenant_id", ""),
            ]

        self._backfill_queryset(
            label="TeachingAssignment",
            queryset=queryset,
            candidate_fn=candidates,
            model=TeachingAssignment,
        )

    def _backfill_enrollments(self):
        queryset = Enrollment.objects.select_related("student", "classroom")

        def candidates(obj):
            return [
                getattr(obj.student, "tenant_id", ""),
                getattr(obj.classroom, "tenant_id", ""),
            ]

        self._backfill_queryset(
            label="Enrollment",
            queryset=queryset,
            candidate_fn=candidates,
            model=Enrollment,
        )

    def _backfill_attendance_records(self):
        queryset = AttendanceRecord.objects.select_related("enrollment")

        def candidates(obj):
            return [getattr(obj.enrollment, "tenant_id", "")]

        self._backfill_queryset(
            label="AttendanceRecord",
            queryset=queryset,
            candidate_fn=candidates,
            model=AttendanceRecord,
        )

    def _backfill_assessment_periods(self):
        queryset = AssessmentPeriod.objects.select_related("academic_year")

        def candidates(obj):
            return [getattr(obj.academic_year, "tenant_id", "")]

        self._backfill_queryset(
            label="AssessmentPeriod",
            queryset=queryset,
            candidate_fn=candidates,
            model=AssessmentPeriod,
        )

    def _backfill_assessment_components(self):
        queryset = AssessmentComponent.objects.select_related("period", "grade_subject")

        def candidates(obj):
            return [
                getattr(obj.period, "tenant_id", ""),
                getattr(obj.grade_subject, "tenant_id", ""),
            ]

        self._backfill_queryset(
            label="AssessmentComponent",
            queryset=queryset,
            candidate_fn=candidates,
            model=AssessmentComponent,
        )

    def _backfill_assessments(self):
        queryset = Assessment.objects.select_related("student", "teaching_assignment", "period")

        def candidates(obj):
            return [
                getattr(obj.student, "tenant_id", ""),
                getattr(obj.teaching_assignment, "tenant_id", ""),
                getattr(obj.period, "tenant_id", ""),
            ]

        self._backfill_queryset(
            label="Assessment",
            queryset=queryset,
            candidate_fn=candidates,
            model=Assessment,
        )

    def _backfill_subject_period_results(self):
        queryset = SubjectPeriodResult.objects.select_related("student", "teaching_assignment", "period")

        def candidates(obj):
            return [
                getattr(obj.student, "tenant_id", ""),
                getattr(obj.teaching_assignment, "tenant_id", ""),
                getattr(obj.period, "tenant_id", ""),
            ]

        self._backfill_queryset(
            label="SubjectPeriodResult",
            queryset=queryset,
            candidate_fn=candidates,
            model=SubjectPeriodResult,
        )

    def _backfill_curriculum_plans(self):
        queryset = SubjectCurriculumPlan.objects.select_related("grade_subject")

        def candidates(obj):
            return [getattr(obj.grade_subject, "tenant_id", "")]

        self._backfill_queryset(
            label="SubjectCurriculumPlan",
            queryset=queryset,
            candidate_fn=candidates,
            model=SubjectCurriculumPlan,
        )

    def _backfill_learning_outcomes(self):
        queryset = LearningOutcome.objects.all()

        def candidates(obj):
            return []

        self._backfill_queryset(
            label="LearningOutcome",
            queryset=queryset,
            candidate_fn=candidates,
            model=LearningOutcome,
        )

    def _backfill_competency_outcomes(self):
        queryset = CompetencyOutcome.objects.select_related("outcome")

        def candidates(obj):
            return [getattr(obj.outcome, "tenant_id", "")]

        self._backfill_queryset(
            label="CompetencyOutcome",
            queryset=queryset,
            candidate_fn=candidates,
            model=CompetencyOutcome,
        )

    def _backfill_lessons(self):
        queryset = Lesson.objects.select_related("offering")

        def candidates(obj):
            return [getattr(obj.offering, "tenant_id", "")]

        self._backfill_queryset(
            label="Lesson",
            queryset=queryset,
            candidate_fn=candidates,
            model=Lesson,
        )

    def _backfill_assignments(self):
        queryset = Assignment.objects.select_related("offering")

        def candidates(obj):
            return [getattr(obj.offering, "tenant_id", "")]

        self._backfill_queryset(
            label="Assignment",
            queryset=queryset,
            candidate_fn=candidates,
            model=Assignment,
        )

    def _backfill_submissions(self):
        queryset = Submission.objects.select_related("assignment", "student")

        def candidates(obj):
            return [
                getattr(obj.assignment, "tenant_id", ""),
                getattr(obj.student, "tenant_id", ""),
            ]

        self._backfill_queryset(
            label="Submission",
            queryset=queryset,
            candidate_fn=candidates,
            model=Submission,
        )

    def _backfill_reports(self):
        queryset = Report.objects.select_related("student")

        def candidates(obj):
            return [getattr(obj.student, "tenant_id", "")]

        self._backfill_queryset(
            label="Report",
            queryset=queryset,
            candidate_fn=candidates,
            model=Report,
        )

    def _backfill_progressions(self):
        queryset = Progression.objects.select_related("student")

        def candidates(obj):
            return [getattr(obj.student, "tenant_id", "")]

        self._backfill_queryset(
            label="Progression",
            queryset=queryset,
            candidate_fn=candidates,
            model=Progression,
        )

    def _backfill_student_competencies(self):
        queryset = StudentCompetency.objects.select_related("student")

        def candidates(obj):
            return [getattr(obj.student, "tenant_id", "")]

        self._backfill_queryset(
            label="StudentCompetency",
            queryset=queryset,
            candidate_fn=candidates,
            model=StudentCompetency,
        )

    def _backfill_student_guardians(self):
        queryset = StudentGuardian.objects.select_related("student", "guardian")

        def candidates(obj):
            return [
                getattr(obj.student, "tenant_id", ""),
                getattr(obj.guardian, "tenant_id", ""),
            ]

        self._backfill_queryset(
            label="StudentGuardian",
            queryset=queryset,
            candidate_fn=candidates,
            model=StudentGuardian,
        )

    def _backfill_student_outcomes(self):
        queryset = StudentOutcome.objects.select_related("student", "outcome")

        def candidates(obj):
            return [
                getattr(obj.student, "tenant_id", ""),
                getattr(obj.outcome, "tenant_id", ""),
            ]

        self._backfill_queryset(
            label="StudentOutcome",
            queryset=queryset,
            candidate_fn=candidates,
            model=StudentOutcome,
        )

    def _backfill_invoices(self):
        queryset = Invoice.objects.select_related("student", "school")

        def candidates(obj):
            return [
                getattr(obj.student, "tenant_id", ""),
                getattr(obj.school, "tenant_id", ""),
            ]

        self._backfill_queryset(
            label="Invoice",
            queryset=queryset,
            candidate_fn=candidates,
            model=Invoice,
        )

    def _backfill_payments(self):
        queryset = Payment.objects.select_related("invoice")

        def candidates(obj):
            return [getattr(obj.invoice, "tenant_id", "")]

        self._backfill_queryset(
            label="Payment",
            queryset=queryset,
            candidate_fn=candidates,
            model=Payment,
        )

    def _backfill_announcements(self):
        queryset = Announcement.objects.select_related("school", "classroom", "author__school_profile")

        def candidates(obj):
            return [
                getattr(obj.classroom, "tenant_id", ""),
                getattr(obj.school, "tenant_id", ""),
                getattr(getattr(obj.author, "school_profile", None), "tenant_id", ""),
            ]

        self._backfill_queryset(
            label="Announcement",
            queryset=queryset,
            candidate_fn=candidates,
            model=Announcement,
        )

    def _backfill_assessment_outcome_maps(self):
        queryset = AssessmentOutcomeMap.objects.select_related("component", "outcome")

        def candidates(obj):
            return [
                getattr(obj.component, "tenant_id", ""),
                getattr(obj.outcome, "tenant_id", ""),
            ]

        self._backfill_queryset(
            label="AssessmentOutcomeMap",
            queryset=queryset,
            candidate_fn=candidates,
            model=AssessmentOutcomeMap,
        )

    def _backfill_audit_events(self):
        if not self._table_exists(AuditEvent):
            self._record(label="AuditEvent", scanned=0, updated=0, missing=0, conflicts=0)
            self._add_sample("AuditEvent", "-", f"table {AuditEvent._meta.db_table} missing")
            return

        queryset = AuditEvent.objects.all()
        by_resource = defaultdict(list)
        for obj_id, resource in queryset.filter(tenant_id="").values_list("object_id", "resource"):
            by_resource[resource].append(obj_id)

        resource_map = {
            "report": Report,
            "attendance_record": AttendanceRecord,
            "announcement": Announcement,
            "invoice": Invoice,
            "payment": Payment,
            "assessment": Assessment,
        }
        tenant_by_resource_id = {}
        for resource, model in resource_map.items():
            object_ids = by_resource.get(resource, [])
            if not object_ids:
                continue
            if not self._table_exists(model):
                continue
            objects = model.objects.in_bulk(object_ids)
            tenant_by_resource_id[resource] = {
                obj_id: _normalize(getattr(obj, "tenant_id", "")) for obj_id, obj in objects.items()
            }

        def candidates(obj):
            mapping = tenant_by_resource_id.get(obj.resource, {})
            return [mapping.get(obj.object_id, "")]

        self._backfill_queryset(
            label="AuditEvent",
            queryset=queryset,
            candidate_fn=candidates,
            model=AuditEvent,
        )

    def _backfill_audit_alerts(self):
        if not self._table_exists(AuditAlert):
            self._record(label="AuditAlert", scanned=0, updated=0, missing=0, conflicts=0)
            self._add_sample("AuditAlert", "-", f"table {AuditAlert._meta.db_table} missing")
            return

        event_rows = []
        if self._table_exists(AuditEvent):
            event_rows = (
                AuditEvent.objects.exclude(tenant_id="")
                .order_by("-created_at")
                .values_list("resource", "username", "tenant_id")
            )
        by_resource_user = {}
        by_resource = {}
        for resource, username, tenant in event_rows:
            tenant = _normalize(tenant)
            if not tenant:
                continue
            if resource and username and (resource, username) not in by_resource_user:
                by_resource_user[(resource, username)] = tenant
            if resource and resource not in by_resource:
                by_resource[resource] = tenant

        queryset = AuditAlert.objects.all()

        def candidates(obj):
            return [
                by_resource_user.get((obj.resource, obj.username), ""),
                by_resource.get(obj.resource, ""),
            ]

        self._backfill_queryset(
            label="AuditAlert",
            queryset=queryset,
            candidate_fn=candidates,
            model=AuditAlert,
        )

    def _backfill_local_curricula(self):
        queryset = LocalCurriculum.objects.all()

        def candidates(obj):
            return []

        self._backfill_queryset(
            label="LocalCurriculum",
            queryset=queryset,
            candidate_fn=candidates,
            model=LocalCurriculum,
        )

    def _backfill_events(self):
        if not self._table_exists(Event):
            self._record(label="Event", scanned=0, updated=0, missing=0, conflicts=0)
            self._add_sample("Event", "-", f"table {Event._meta.db_table} missing")
            return

        queryset = Event.objects.all()
        blank_events = list(queryset.filter(tenant_id="").values_list("id", "payload"))

        school_ids = set()
        student_ids = set()
        report_ids = set()
        assessment_ids = set()

        for _, payload in blank_events:
            if not isinstance(payload, dict):
                continue
            school_ids.update({payload.get("school_id"), payload.get("escola_id")})
            student_ids.update({payload.get("student_id"), payload.get("aluno_id")})
            report_ids.update({payload.get("report_id"), payload.get("relatorio_id")})
            assessment_ids.update({payload.get("assessment_id"), payload.get("avaliacao_id")})

        school_ids.discard(None)
        student_ids.discard(None)
        report_ids.discard(None)
        assessment_ids.discard(None)

        schools = School.objects.in_bulk(list(school_ids)) if self._table_exists(School) else {}
        students = Student.objects.in_bulk(list(student_ids)) if self._table_exists(Student) else {}
        reports = Report.objects.in_bulk(list(report_ids)) if self._table_exists(Report) else {}
        assessments = Assessment.objects.in_bulk(list(assessment_ids)) if self._table_exists(Assessment) else {}

        tenant_by_school = {pk: _normalize(obj.tenant_id) for pk, obj in schools.items()}
        tenant_by_student = {pk: _normalize(obj.tenant_id) for pk, obj in students.items()}
        tenant_by_report = {pk: _normalize(obj.tenant_id) for pk, obj in reports.items()}
        tenant_by_assessment = {pk: _normalize(obj.tenant_id) for pk, obj in assessments.items()}

        payloads_by_id = {event_id: payload for event_id, payload in blank_events}

        def candidates(obj):
            payload = payloads_by_id.get(obj.pk, {})
            if not isinstance(payload, dict):
                return []
            direct = payload.get("tenant_id") or payload.get("tenant")
            if direct:
                return [direct]
            school_id = payload.get("school_id") or payload.get("escola_id")
            student_id = payload.get("student_id") or payload.get("aluno_id")
            report_id = payload.get("report_id") or payload.get("relatorio_id")
            assessment_id = payload.get("assessment_id") or payload.get("avaliacao_id")
            return [
                tenant_by_school.get(school_id, ""),
                tenant_by_student.get(student_id, ""),
                tenant_by_report.get(report_id, ""),
                tenant_by_assessment.get(assessment_id, ""),
            ]

        self._backfill_queryset(
            label="Event",
            queryset=queryset,
            candidate_fn=candidates,
            model=Event,
        )
