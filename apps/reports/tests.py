from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework.test import APITestCase

from apps.academic.models import Student
from apps.assessment.models import AssessmentPeriod, SubjectPeriodResult
from apps.curriculum.models import CurriculumArea, Subject
from apps.school.models import (
    AcademicYear,
    AttendanceRecord,
    Classroom,
    Enrollment,
    Grade,
    GradeSubject,
    Invoice,
    ManagementAssignment,
    Payment,
    School,
    Teacher,
    TeachingAssignment,
    UserProfile,
)
from .models import Report


class RelatorioModelTests(TestCase):
    def setUp(self):
        self.student = Student.objects.create(
            name="Lina",
            birth_date=date(2015, 3, 12),
            grade=1,
            cycle=1,
        )

    def test_relatorio_de_aluno_exige_aluno(self):
        with self.assertRaises(ValidationError):
            Report.objects.create(
                titulo="Relatório sem student",
                tipo="student",
                period="2026-2027",
                conteudo={"total": 1},
            )

    def test_relatorio_de_escola_nao_aceita_aluno(self):
        with self.assertRaises(ValidationError):
            Report.objects.create(
                titulo="Relatório de school",
                tipo="school",
                period="2026-2027",
                conteudo={"total": 1},
                student=self.student,
            )

    def test_relatorio_gera_codigo_e_assinatura_de_verificacao(self):
        report = Report.objects.create(
            titulo="Relatório válido",
            tipo="student",
            period="2026-2027",
            conteudo={"total": 1},
            student=self.student,
        )

        self.assertTrue(report.verification_code.startswith("RPT-"))
        self.assertTrue(report.serial_number.startswith("ALN-"))
        self.assertEqual(len(report.verification_hash), 64)
        self.assertTrue(report.verify_integrity())


class ReportGenerationApiTests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.tenant_id = "tenant-01"
        self.user = user_model.objects.create_user(username="director", password="secret123")
        self.teacher_user = user_model.objects.create_user(username="teacher", password="secret123")

        self.school = School.objects.create(code="ESC-01", name="Escola Primaria Central")
        self.academic_year = AcademicYear.objects.create(
            code="2026-2027",
            start_date=date(2026, 2, 1),
            end_date=date(2026, 12, 15),
            active=True,
        )
        self.grade = Grade.objects.create(number=2, cycle=1)
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            tenant_id=self.tenant_id,
            school=self.school,
            name="Prof. Carla",
            specialty="Matematica",
        )
        self.classroom = Classroom.objects.create(
            name="2A",
            tenant_id=self.tenant_id,
            school=self.school,
            grade=self.grade,
            cycle=1,
            academic_year=self.academic_year,
            lead_teacher=self.teacher,
        )
        self.student = Student.objects.create(
            name="Beto",
            tenant_id=self.tenant_id,
            birth_date=date(2015, 5, 20),
            grade=2,
            cycle=1,
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            classroom=self.classroom,
            tenant_id=self.tenant_id,
        )

        self.profile = self.user.school_profile
        self.profile.role = "school_director"
        self.profile.school = self.school
        self.profile.tenant_id = self.tenant_id
        self.profile.active = True
        self.profile.save()

        area = CurriculumArea.objects.create(name="Ciencias")
        self.subject = Subject.objects.create(name="Matematica", area=area, cycle=1)
        self.grade_subject = GradeSubject.objects.create(
            academic_year=self.academic_year,
            grade=self.grade,
            subject=self.subject,
            weekly_workload=5,
        )
        self.assignment = TeachingAssignment.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            tenant_id=self.tenant_id,
            grade_subject=self.grade_subject,
        )
        self.period_1 = AssessmentPeriod.objects.create(
            academic_year=self.academic_year,
            name="1o Trimestre",
            order=1,
            start_date=date(2026, 2, 1),
            end_date=date(2026, 4, 30),
            active=True,
        )
        self.period_2 = AssessmentPeriod.objects.create(
            academic_year=self.academic_year,
            name="2o Trimestre",
            order=2,
            start_date=date(2026, 5, 1),
            end_date=date(2026, 7, 31),
            active=True,
        )
        SubjectPeriodResult.objects.create(
            student=self.student,
            teaching_assignment=self.assignment,
            period=self.period_1,
            final_average=Decimal("15.50"),
            assessments_counted=3,
        )
        SubjectPeriodResult.objects.create(
            student=self.student,
            teaching_assignment=self.assignment,
            period=self.period_2,
            final_average=Decimal("16.00"),
            assessments_counted=2,
        )
        AttendanceRecord.objects.create(
            enrollment=self.enrollment,
            tenant_id=self.tenant_id,
            lesson_date=date(2026, 3, 10),
            status="present",
        )
        AttendanceRecord.objects.create(
            enrollment=self.enrollment,
            tenant_id=self.tenant_id,
            lesson_date=date(2026, 3, 11),
            status="absent",
        )
        ManagementAssignment.objects.create(
            teacher=self.teacher,
            school=self.school,
            academic_year=self.academic_year,
            tenant_id=self.tenant_id,
            role="school_director",
            active=True,
        )
        invoice = Invoice.objects.create(
            student=self.student,
            school=self.school,
            tenant_id=self.tenant_id,
            reference="FAT-001",
            description="Propina",
            amount=Decimal("1500.00"),
            due_date=date(2026, 3, 30),
            status="issued",
        )
        Payment.objects.create(
            invoice=invoice,
            tenant_id=self.tenant_id,
            amount=Decimal("500.00"),
            payment_date=date(2026, 3, 20),
            method="cash",
            reference="PAG-001",
        )

        self.client.force_authenticate(self.user)

    def test_generate_student_declaration_persists_report(self):
        response = self.client.post(
            "/api/v1/reports/reports/generate/",
            {
                "report_kind": "student_declaration",
                "student": self.student.id,
                "academic_year": self.academic_year.id,
                "persist": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        report = Report.objects.get(pk=response.data["id"])
        self.assertEqual(report.type, "student")
        self.assertEqual(report.student, self.student)
        self.assertEqual(report.content["report_kind"], "student_declaration")
        self.assertEqual(report.content["student_snapshot"]["name"], "Beto")

    def test_generate_school_statistics_returns_expected_counts(self):
        response = self.client.post(
            "/api/v1/reports/reports/generate/",
            {
                "report_kind": "school_statistics",
                "academic_year": self.academic_year.id,
                "persist": False,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        summary = response.data["summary"]
        self.assertEqual(summary["students"], 1)
        self.assertEqual(summary["teachers"], 1)
        self.assertEqual(summary["classrooms"], 1)
        self.assertEqual(summary["enrollments"], 1)
        self.assertEqual(summary["directors"], 1)
        self.assertEqual(summary["payments"], 1)

    def test_generate_quarterly_grade_sheet_returns_rows(self):
        response = self.client.post(
            "/api/v1/reports/reports/generate/",
            {
                "report_kind": "quarterly_grade_sheet",
                "academic_year": self.academic_year.id,
                "classroom": self.classroom.id,
                "period_order": 1,
                "persist": False,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["metadata"]["period_label"], "Trimestre 1")
        self.assertEqual(len(response.data["rows"]), 1)
        self.assertEqual(response.data["rows"][0]["student_name"], "Beto")
        self.assertEqual(response.data["rows"][0]["subjects"][0]["subject"], "Matematica")
        self.assertEqual(response.data["rows"][0]["overall_average"], 15.5)

    def test_generate_students_by_grade_year_classroom_returns_scoped_students(self):
        response = self.client.post(
            "/api/v1/reports/reports/generate/",
            {
                "report_kind": "students_by_grade_year_classroom",
                "academic_year": self.academic_year.id,
                "classroom": self.classroom.id,
                "persist": False,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["summary"]["total"], 1)
        self.assertEqual(response.data["rows"][0]["classroom"], "2A")
        self.assertEqual(response.data["rows"][0]["academic_year"], "2026-2027")

    def test_generate_rejects_grade_sheet_without_scope(self):
        response = self.client.post(
            "/api/v1/reports/reports/generate/",
            {
                "report_kind": "annual_grade_sheet",
                "academic_year": self.academic_year.id,
                "persist": False,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("classroom", response.data["error"]["details"])

    def test_create_endpoint_rejects_manual_issue(self):
        response = self.client.post(
            "/api/v1/reports/reports/",
            {
                "title": "Falso",
                "type": "school",
                "period": "2026-2027",
                "content": {"fake": True},
            },
            format="json",
        )

        self.assertEqual(response.status_code, 405)

    def test_verify_endpoint_accepts_authentic_document(self):
        response = self.client.post(
            "/api/v1/reports/reports/generate/",
            {
                "report_kind": "student_declaration",
                "student": self.student.id,
                "academic_year": self.academic_year.id,
                "persist": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        verify_response = self.client.get(
            f"/api/v1/reports/reports/verify/?code={response.data['verification_code']}&hash={response.data['verification_hash']}"
        )

        self.assertEqual(verify_response.status_code, 200)
        self.assertTrue(verify_response.data["valid"])
        self.assertEqual(verify_response.data["title"], response.data["title"])

    def test_verify_endpoint_rejects_invalid_signature(self):
        response = self.client.post(
            "/api/v1/reports/reports/generate/",
            {
                "report_kind": "student_declaration",
                "student": self.student.id,
                "academic_year": self.academic_year.id,
                "persist": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        verify_response = self.client.get(
            f"/api/v1/reports/reports/verify/?code={response.data['verification_code']}&hash=INVALIDHASH"
        )

        self.assertEqual(verify_response.status_code, 409)
        self.assertFalse(verify_response.data["valid"])

    def test_export_html_and_pdf_endpoints_work(self):
        response = self.client.post(
            "/api/v1/reports/reports/generate/",
            {
                "report_kind": "student_certificate",
                "student": self.student.id,
                "academic_year": self.academic_year.id,
                "persist": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        report_id = response.data["id"]

        html_response = self.client.get(f"/api/v1/reports/reports/{report_id}/export/?format=html")
        pdf_response = self.client.get(f"/api/v1/reports/reports/{report_id}/export/?format=pdf")

        self.assertEqual(html_response.status_code, 200)
        self.assertIn("text/html", html_response["Content-Type"])
        self.assertIn(response.data["serial_number"], html_response.content.decode("utf-8"))

        self.assertEqual(pdf_response.status_code, 200)
        self.assertIn("application/pdf", pdf_response["Content-Type"])
        self.assertTrue(pdf_response.content.startswith(b"%PDF-1.4"))
