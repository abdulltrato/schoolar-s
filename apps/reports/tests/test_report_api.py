from datetime import date

from apps.reports.models import Report
from .base import ReportApiBase


class ReportGenerationApiTests(ReportApiBase):
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

        html_response = self.client.get(f"/api/v1/reports/reports/{report_id}/export/?export_format=html")
        pdf_response = self.client.get(f"/api/v1/reports/reports/{report_id}/export/?export_format=pdf")

        self.assertEqual(html_response.status_code, 200)
        self.assertIn("text/html", html_response["Content-Type"])
        self.assertIn(response.data["serial_number"], html_response.content.decode("utf-8"))

        self.assertEqual(pdf_response.status_code, 200)
        self.assertIn("application/pdf", pdf_response["Content-Type"])
        self.assertTrue(pdf_response.content.startswith(b"%PDF-1.4"))
