import re

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.academic.models import Student, StudentOutcome
from apps.assessment.models import AssessmentOutcomeMap
from apps.school.models import AcademicYear, Classroom


class Command(BaseCommand):
    help = "Recalculate student learning outcomes based on assessment mappings."

    def add_arguments(self, parser):
        parser.add_argument("--tenant-id", help="Filter by tenant id.")
        parser.add_argument("--student-id", type=int, help="Recalculate a single student.")
        parser.add_argument("--classroom-id", type=int, help="Recalculate students in a classroom.")
        parser.add_argument("--academic-year", help="Academic year id or code (YYYY-YYYY).")
        parser.add_argument("--component-id", type=int, help="Restrict to a component id.")
        parser.add_argument("--outcome-id", type=int, action="append", help="Restrict to outcome id(s).")
        parser.add_argument("--dry-run", action="store_true", help="Show what would change without updating.")
        parser.add_argument("--batch-size", type=int, default=200, help="Batch size for processing students.")

    def handle(self, *args, **options):
        tenant_id = (options.get("tenant_id") or "").strip()
        student_id = options.get("student_id")
        classroom_id = options.get("classroom_id")
        academic_year = options.get("academic_year")
        component_id = options.get("component_id")
        outcome_ids = options.get("outcome_id") or []
        dry_run = options.get("dry_run")
        batch_size = max(1, options.get("batch_size") or 200)

        year = None
        if academic_year:
            year = self._resolve_academic_year(academic_year, tenant_id)

        students_qs = self._build_students_queryset(
            tenant_id=tenant_id,
            student_id=student_id,
            classroom_id=classroom_id,
            academic_year=year,
        )
        total_students = students_qs.count()

        mapping_qs = self._build_mapping_queryset(
            tenant_id=tenant_id,
            component_id=component_id,
            outcome_ids=outcome_ids,
            academic_year=year,
            classroom_id=classroom_id,
        )
        outcome_ids = list(mapping_qs.values_list("outcome_id", flat=True).distinct())

        if not outcome_ids:
            self.stdout.write("No outcome mappings found for the given filters.")
            return

        processed = 0
        with transaction.atomic():
            for student in students_qs.iterator(chunk_size=batch_size):
                StudentOutcome.recalculate_for_outcomes(student=student, outcome_ids=outcome_ids)
                processed += 1

            if dry_run:
                transaction.set_rollback(True)

        self.stdout.write(
            f"Recalculated outcomes for {processed}/{total_students} students "
            f"using {len(outcome_ids)} outcomes. dry_run={dry_run}"
        )

    def _resolve_academic_year(self, value, tenant_id):
        value = str(value).strip()
        if value.isdigit():
            return AcademicYear.objects.filter(pk=int(value)).first()
        if not re.fullmatch(r"\d{4}-\d{4}", value):
            raise SystemExit("Invalid academic_year format. Use id or YYYY-YYYY.")

        queryset = AcademicYear.objects.filter(code=value)
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        matches = list(queryset[:2])
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            raise SystemExit("Academic year code is ambiguous. Provide --tenant-id.")
        raise SystemExit("Academic year not found.")

    def _build_students_queryset(self, *, tenant_id, student_id, classroom_id, academic_year):
        if student_id:
            queryset = Student.objects.filter(pk=student_id)
        else:
            queryset = Student.objects.all()

        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)

        if classroom_id:
            queryset = queryset.filter(enrollment__classroom_id=classroom_id).distinct()
        elif academic_year:
            queryset = queryset.filter(enrollment__classroom__academic_year=academic_year).distinct()

        return queryset

    def _build_mapping_queryset(self, *, tenant_id, component_id, outcome_ids, academic_year, classroom_id):
        queryset = AssessmentOutcomeMap.objects.filter(active=True)
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        if component_id:
            queryset = queryset.filter(component_id=component_id)
        if outcome_ids:
            queryset = queryset.filter(outcome_id__in=outcome_ids)
        if academic_year:
            queryset = queryset.filter(component__period__academic_year=academic_year)
        if classroom_id:
            classroom = Classroom.objects.filter(pk=classroom_id).select_related("academic_year", "grade").first()
            if classroom:
                queryset = queryset.filter(
                    component__grade_subject__grade=classroom.grade,
                    component__grade_subject__academic_year=classroom.academic_year,
                )
        return queryset
