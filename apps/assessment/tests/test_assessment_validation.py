from datetime import date
from django.core.files.uploadedfile import SimpleUploadedFile
from decimal import Decimal

from django.core.exceptions import ValidationError

from apps.assessment.models import Assessment
from .base import AssessmentTestCaseBase


class AssessmentValidationTests(AssessmentTestCaseBase):
    def test_rejeita_avaliacao_de_aluno_nao_matriculado_na_turma(self):
        outro_aluno = self.student.__class__.objects.create(
            name="Beto",
            birth_date=date(2016, 5, 1),
            grade=2,
            cycle=1,
            tenant_id=self.school.tenant_id,
            identification_document=SimpleUploadedFile("id-beto.pdf", b"%PDF-1.4 test"),
            previous_certificate=SimpleUploadedFile("cert-beto.pdf", b"%PDF-1.4 test"),
        )

        with self.assertRaises(ValidationError):
            Assessment.objects.create(
                student=outro_aluno,
                teaching_assignment=self.alocacao,
                period=self.period,
                component=self.componente_teste,
                tipo="teste",
                data=date(2026, 3, 1),
                score=14,
            )

    def test_rejeita_avaliacao_com_competencia_de_outra_disciplina(self):
        with self.assertRaises(ValidationError):
            Assessment.objects.create(
                student=self.student,
                teaching_assignment=self.alocacao,
                period=self.period,
                component=self.componente_teste,
                competency=self.competencia_outra_disciplina,
                tipo="teste",
                data=date(2026, 3, 1),
                score=15,
            )

    def test_rejeita_avaliacao_com_nota_acima_da_componente(self):
        with self.assertRaises(ValidationError):
            Assessment.objects.create(
                student=self.student,
                teaching_assignment=self.alocacao,
                period=self.period,
                component=self.componente_teste,
                competency=self.competency,
                tipo="teste",
                data=date(2026, 3, 1),
                score=21,
            )
