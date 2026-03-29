from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.assessment.scheduler import schedule_assessments
from apps.assessment.tests.base import AssessmentTestCaseBase
from apps.school.models import Enrollment, PaymentPlan


class ScheduleAssessmentsTests(AssessmentTestCaseBase, TestCase):
    def setUp(self):
        super().setUp()
        # Configura taxas de exame na matrícula existente
        enrollment = Enrollment.objects.get(student=self.student, classroom=self.classroom)
        enrollment.exam_fee = Decimal("2500.00")
        enrollment.save(update_fields=["exam_fee"])

    def test_agenda_exame_para_turma_e_fatura_taxa(self):
        created = schedule_assessments(
            teaching_assignment_id=self.alocacao.id,
            component_id=self.componente_exame.id,
            date_avaliacao=date(2026, 6, 1),
            target="turma",
            exam_tipo="exam_regular",
        )
        self.assertEqual(created, 1)

        plano = PaymentPlan.objects.get(enrollment__student=self.student, type="exam_regular")
        self.assertEqual(plano.status, "invoiced")
        self.assertIsNotNone(plano.invoice)
        self.assertEqual(plano.invoice.amount, plano.amount)

    def test_agenda_teste_para_um_aluno_sem_fatura(self):
        created = schedule_assessments(
            teaching_assignment_id=self.alocacao.id,
            component_id=self.componente_teste.id,
            date_avaliacao=date(2026, 3, 10),
            target="individual",
            student_ids=[self.student.id],
        )
        self.assertEqual(created, 1)
        planos = PaymentPlan.objects.filter(enrollment__student=self.student, type__startswith="exam_")
        self.assertTrue(all(p.status == "scheduled" for p in planos))

    def test_valida_target_e_exam_tipo(self):
        with self.assertRaisesMessage(Exception, "target"):
            schedule_assessments(
                teaching_assignment_id=self.alocacao.id,
                component_id=self.componente_teste.id,
                date_avaliacao=date(2026, 3, 10),
                target="invalido",
                student_ids=[self.student.id],
            )
        with self.assertRaisesMessage(Exception, "exam_tipo"):
            schedule_assessments(
                teaching_assignment_id=self.alocacao.id,
                component_id=self.componente_exame.id,
                date_avaliacao=date(2026, 6, 1),
                target="turma",
                exam_tipo="foo",
            )
