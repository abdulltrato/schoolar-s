from datetime import date
from decimal import Decimal

from apps.assessment.models import Assessment, SubjectPeriodResult
from .base import AssessmentTestCaseBase


class AssessmentResultsTests(AssessmentTestCaseBase):
    def test_calcula_media_ponderada_por_periodo(self):
        Assessment.objects.create(
            student=self.student,
            teaching_assignment=self.alocacao,
            period=self.period,
            component=self.componente_teste,
            competency=self.competency,
            tipo="teste",
            data=date(2026, 3, 1),
            score=Decimal("10.0"),
        )
        Assessment.objects.create(
            student=self.student,
            teaching_assignment=self.alocacao,
            period=self.period,
            component=self.componente_exame,
            competency=self.competency,
            tipo="exame",
            data=date(2026, 4, 20),
            score=Decimal("20.0"),
        )

        resultado = SubjectPeriodResult.recalcular(
            student=self.student,
            teaching_assignment=self.alocacao,
            period=self.period,
        )

        self.assertEqual(resultado.assessments_counted, 2)
        self.assertEqual(resultado.final_average, Decimal("16.00"))

    def test_atualiza_resultado_automaticamente_ao_salvar_avaliacoes(self):
        Assessment.objects.create(
            student=self.student,
            teaching_assignment=self.alocacao,
            period=self.period,
            component=self.componente_teste,
            competency=self.competency,
            tipo="teste",
            data=date(2026, 3, 1),
            score=Decimal("10.0"),
        )
        Assessment.objects.create(
            student=self.student,
            teaching_assignment=self.alocacao,
            period=self.period,
            component=self.componente_exame,
            competency=self.competency,
            tipo="exame",
            data=date(2026, 4, 20),
            score=Decimal("20.0"),
        )

        resultado = SubjectPeriodResult.objects.get(
            student=self.student,
            teaching_assignment=self.alocacao,
            period=self.period,
        )

        self.assertEqual(resultado.assessments_counted, 2)
        self.assertEqual(resultado.final_average, Decimal("16.00"))

    def test_remove_resultado_quando_ultima_avaliacao_e_apagada(self):
        assessment = Assessment.objects.create(
            student=self.student,
            teaching_assignment=self.alocacao,
            period=self.period,
            component=self.componente_teste,
            competency=self.competency,
            tipo="teste",
            data=date(2026, 3, 1),
            score=Decimal("10.0"),
        )

        self.assertTrue(
            SubjectPeriodResult.objects.filter(
                student=self.student,
                teaching_assignment=self.alocacao,
                period=self.period,
            ).exists()
        )

        assessment.delete()

        self.assertFalse(
            SubjectPeriodResult.objects.filter(
                student=self.student,
                teaching_assignment=self.alocacao,
                period=self.period,
            ).exists()
        )
