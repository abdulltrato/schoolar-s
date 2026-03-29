from datetime import date

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from apps.academic.models import Student
from apps.reports.models import Report


class ReportModelTests(TestCase):
    def setUp(self):
        self.student = Student.objects.create(
            name="Lina",
            birth_date=date(2015, 3, 12),
            grade=1,
            cycle=1,
            tenant_id="tenant-esc-01",
            identification_document=SimpleUploadedFile("id-lina.pdf", b"%PDF-1.4 test"),
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
