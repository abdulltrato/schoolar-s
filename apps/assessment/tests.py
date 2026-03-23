from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.academic.models import Student
from apps.curriculum.models import CurriculumArea, Competency, Subject
from apps.school.models import TeachingAssignment, AcademicYear, Grade, GradeSubject, School, Enrollment, Teacher, Classroom
from .models import Assessment, AssessmentComponent, AssessmentPeriod, SubjectPeriodResult


class AvaliacaoModelTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(code="ESC-01", name="School Primaria Central")
        user = get_user_model().objects.create_user(username="prof", password="secret")
        self.teacher = Teacher.objects.create(user=user, name="Prof. Ana", school=self.school)
        self.academic_year = AcademicYear.objects.create(
            code="2026-2027",
            start_date=date(2026, 2, 1),
            end_date=date(2026, 12, 15),
            active=True,
        )
        self.period = AssessmentPeriod.objects.create(
            academic_year=self.academic_year,
            name="1o Trimestre",
            order=1,
            start_date=date(2026, 2, 1),
            end_date=date(2026, 4, 30),
        )
        self.grade = Grade.objects.create(number=2, cycle=1)
        self.classroom = Classroom.objects.create(
            name="Classroom A",
            school=self.school,
            grade=self.grade,
            cycle=1,
            academic_year=self.academic_year,
            lead_teacher=self.teacher,
        )
        self.student = Student.objects.create(
            name="Ana",
            birth_date=date(2016, 2, 1),
            grade=2,
            cycle=1,
        )
        Enrollment.objects.create(student=self.student, classroom=self.classroom)

        area = CurriculumArea.objects.create(name="Ciencias Naturais")
        self.subject = Subject.objects.create(name="Matematica", area=area, cycle=1)
        self.outra_disciplina = Subject.objects.create(name="Historia", area=area, cycle=1)
        self.grade_subject = GradeSubject.objects.create(
            academic_year=self.academic_year,
            grade=self.grade,
            subject=self.subject,
        )
        self.alocacao = TeachingAssignment.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            grade_subject=self.grade_subject,
        )
        self.componente_teste = AssessmentComponent.objects.create(
            period=self.period,
            grade_subject=self.grade_subject,
            tipo="teste",
            name="Teste 1",
            weight=Decimal("40.00"),
            max_score=Decimal("20.00"),
        )
        self.componente_exame = AssessmentComponent.objects.create(
            period=self.period,
            grade_subject=self.grade_subject,
            tipo="exame",
            name="Exame Final",
            weight=Decimal("60.00"),
            max_score=Decimal("20.00"),
        )
        self.competency = Competency.objects.create(
            name="Resolver operacoes basicas",
            area="saber_cientifico_tecnologico",
            cycle=1,
            subject=self.subject,
        )
        self.competencia_outra_disciplina = Competency.objects.create(
            name="Interpretar factos historicos",
            area="linguagem_comunicacao",
            cycle=1,
            subject=self.outra_disciplina,
        )

    def test_rejeita_avaliacao_de_aluno_nao_matriculado_na_turma(self):
        outro_aluno = Student.objects.create(
            name="Beto",
            birth_date=date(2016, 5, 1),
            grade=2,
            cycle=1,
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
