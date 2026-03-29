import html
from decimal import Decimal
from django.utils import timezone
from apps.academic.models import StudentOutcome
from apps.assessment.models import AssessmentPeriod, SubjectPeriodResult


class StudentReportBuilder:
    def __init__(self, *, student, academic_year, report_kind, spec):
        self.student = student
        self.academic_year = academic_year
        self.report_kind = report_kind
        self.spec = spec

    def build(self):
        snapshot = self._student_snapshot()
        content = {"student_snapshot": snapshot, "summary": {}, "rows": [], "metadata": {}}
        if self.report_kind == "student_progress_report":
            content["rows"] = self._progress_rows()

        verification_code = f"RPT-{self.student.id:06d}"
        return {
            "title": self.spec["label"],
            "scope": self.spec["scope"],
            "academic_year": self.academic_year.code if self.academic_year else "",
            "serial_number": f"ALN-{self.student.id:06d}",
            "verification_code": verification_code,
            "verification_hash": self._hash_stub(verification_code),
            "generated_at": timezone.now().isoformat(),
            "content": content,
        }

    def _student_snapshot(self):
        return {
            "name": self.student.name,
            "grade": self.student.grade,
            "cycle": self.student.cycle,
            "tenant_id": self.student.tenant_id,
        }

    def _progress_rows(self):
        rows = []
        outcomes = StudentOutcome.objects.filter(student=self.student, deleted_at__isnull=True)
        for outcome in outcomes:
            rows.append(
                {
                    "outcome": getattr(outcome.outcome, "code", ""),
                    "mastery": float(outcome.mastery_level),
                    "status": outcome.status,
                }
            )
        return rows

    @staticmethod
    def _hash_stub(code: str) -> str:
        return f"{code:0>32}"[:64]
