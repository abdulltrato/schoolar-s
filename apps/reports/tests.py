from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.academic.models import Student
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
