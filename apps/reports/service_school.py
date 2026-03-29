from decimal import Decimal
from django.db.models import Avg, Count, Q
from django.utils import timezone

from apps.academic.models import Student
from apps.assessment.models import Assessment, AssessmentPeriod, SubjectPeriodResult
from apps.school.models import AcademicYear, AttendanceRecord, Classroom, Grade, Invoice, ManagementAssignment, Payment, Teacher


class SchoolReportBuilder:
    def __init__(self, *, academic_year, classroom, period_order, report_kind, spec):
        self.academic_year = academic_year
        self.classroom = classroom
        self.period_order = period_order
        self.report_kind = report_kind
        self.spec = spec

    def build(self):
        if self.report_kind == "school_statistics":
            summary, rows = self._school_statistics()
        elif self.report_kind in {"quarterly_grade_sheet", "semester_grade_sheet", "annual_grade_sheet"}:
            summary, rows = self._grade_sheet()
        elif self.report_kind == "students_list":
            summary, rows = self._students_list()
        else:
            summary, rows = {}, []

        verification_code = f"RPT-SCH-{self.academic_year.id:06d}"
        return {
            "title": self.spec["label"],
            "scope": self.spec["scope"],
            "academic_year": self.academic_year.code if self.academic_year else "",
            "verification_code": verification_code,
            "verification_hash": self._hash_stub(verification_code),
            "generated_at": timezone.now().isoformat(),
            "content": {
                "summary": summary,
                "rows": rows,
                "metadata": {"academic_year": self.academic_year.code if self.academic_year else ""},
            },
        }

    def _school_statistics(self):
        summary = {}
        summary["students"] = Student.objects.filter(enrollment__classroom__academic_year=self.academic_year).distinct().count()
        summary["teachers"] = Teacher.objects.filter(classrooms__academic_year=self.academic_year).distinct().count()
        summary["classrooms"] = Classroom.objects.filter(academic_year=self.academic_year).count()
        summary["enrollments"] = (
            self.academic_year.classroom_set.filter(enrollment__deleted_at__isnull=True).values("enrollment").count()
        )
        summary["directors"] = ManagementAssignment.objects.filter(academic_year=self.academic_year, active=True).count()
        summary["payments"] = Payment.objects.filter(invoice__school__academic_year=self.academic_year).count()
        rows = []
        return summary, rows

    def _grade_sheet(self):
        if not self.classroom:
            raise ValueError("Classroom é obrigatório para pauta.")

        period = None
        if self.period_order:
            period = AssessmentPeriod.objects.filter(academic_year=self.academic_year, order=self.period_order).first()
        results = SubjectPeriodResult.objects.filter(
            teaching_assignment__classroom=self.classroom,
            period=period if period else None,
        ).select_related("student", "teaching_assignment__grade_subject__subject")

        rows = []
        for result in results:
            rows.append(
                {
                    "student_name": result.student.name,
                    "subject": result.teaching_assignment.grade_subject.subject.name,
                    "overall_average": float(result.final_average),
                }
            )
        return {"total": len(rows), "period_label": f"Trimestre {self.period_order or ''}".strip()}, rows

    def _students_list(self):
        qs = Student.objects.filter(enrollment__classroom__academic_year=self.academic_year).select_related()
        rows = [{"student_name": s.name, "grade": s.grade} for s in qs]
        return {"total": len(rows)}, rows

    @staticmethod
    def _hash_stub(code: str) -> str:
        return f"{code:0>32}"[:64]
