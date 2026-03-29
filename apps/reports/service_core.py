import html
from decimal import Decimal
from io import BytesIO

from django.db.models import Avg, Count, Q
from django.utils import timezone

from apps.academic.models import Student, StudentOutcome
from apps.assessment.models import Assessment, AssessmentPeriod, SubjectPeriodResult
from apps.curriculum.models import LearningOutcome
from apps.school.models import AcademicYear, AttendanceRecord, Classroom, Enrollment, Grade, Invoice, ManagementAssignment, Payment, Teacher
from .models import Report
from .service_pdf import render_pdf_from_context
from .service_students import StudentReportBuilder
from .service_school import SchoolReportBuilder


DIRECTOR_ROLES = {
    "homeroom_director": "Diretor de turma",
    "grade_coordinator": "Coordenador de classe",
    "cycle_director": "Diretor de ciclo",
    "deputy_pedagogical_director": "Diretor adjunto pedagógico",
    "school_director": "Diretor da escola",
}


class ReportGenerationServiceCore:
    CATALOG = {
        "student_declaration": {"label": "Declaração do estudante", "scope": "student", "requires": ["student"]},
        "student_certificate": {"label": "Certificado do estudante", "scope": "student", "requires": ["student"]},
        "student_diploma": {"label": "Diploma do estudante", "scope": "student", "requires": ["student"]},
        "student_progress_report": {"label": "Relatório de aproveitamento do estudante", "scope": "student", "requires": ["student"]},
        "school_statistics": {"label": "Relatório estatístico da escola", "scope": "school", "requires": []},
        "quarterly_grade_sheet": {"label": "Pauta trimestral", "scope": "school", "requires": ["academic_year"]},
        "semester_grade_sheet": {"label": "Pauta semestral", "scope": "school", "requires": ["academic_year"]},
        "annual_grade_sheet": {"label": "Pauta anual", "scope": "school", "requires": ["academic_year"]},
        "students_list": {"label": "Lista de estudantes", "scope": "school", "requires": []},
    }

    def list_catalog(self):
        return self.CATALOG

    def generate_report(self, *, report_kind, student=None, academic_year=None, classroom=None, period_order=None, persist=False):
        if report_kind not in self.CATALOG:
            raise ValueError("Tipo de relatório inválido.")

        spec = self.CATALOG[report_kind]
        if spec["scope"] == "student" and not student:
            raise ValueError("Relatório de estudante requer student.")
        if spec["scope"] == "school" and spec["requires"] and not academic_year:
            raise ValueError("Relatório escolar requer academic_year.")

        if spec["scope"] == "student":
            builder = StudentReportBuilder(
                student=student,
                academic_year=academic_year,
                report_kind=report_kind,
                spec=spec,
            )
        else:
            builder = SchoolReportBuilder(
                academic_year=academic_year,
                classroom=classroom,
                period_order=period_order,
                report_kind=report_kind,
                spec=spec,
            )

        context = builder.build()
        if persist:
            report = Report.objects.create(
                title=context["title"],
                type=context["scope"],
                period=context.get("academic_year"),
                content=context["content"],
                student=student if spec["scope"] == "student" else None,
                metadata=context.get("metadata", {}),
                verification_code=context["verification_code"],
                verification_hash=context["verification_hash"],
                serial_number=context.get("serial_number", ""),
            )
            context["id"] = report.id
        return context

    def export_pdf(self, context):
        return render_pdf_from_context(context)

    def export_html(self, context):
        lines = [f"{html.escape(context['title'])}", f"Código: {context['verification_code']}"]
        if "summary" in context:
            lines.append(f"Resumo: {html.escape(str(context['summary']))}")
        return "<br>".join(lines)
