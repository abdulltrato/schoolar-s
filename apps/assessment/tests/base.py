from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from apps.academic.models import Student
from apps.curriculum.models import CurriculumArea, Competency, Subject, SubjectSpecialty
from apps.school.models import (
    AcademicYear,
    Classroom,
    Enrollment,
    Grade,
    GradeSubject,
    School,
    Teacher,
    TeachingAssignment,
)
from apps.assessment.models import AssessmentComponent, AssessmentPeriod


class AssessmentTestCaseBase(TestCase):
    def setUp(self):
        self.school = School.objects.create(code="ESC-01", name="School Primaria Central", tenant_id="tenant-esc-01")
        area = CurriculumArea.objects.create(name="Ciencias Naturais")
        self.subject = Subject.objects.create(name="Matematica", area=area, cycle=1)
        self.outra_disciplina = Subject.objects.create(name="Historia", area=area, cycle=1)
        specialty = SubjectSpecialty.objects.create(subject=self.subject, name="Matematica")
        user = get_user_model().objects.create_user(username="prof", password="secret")
        self.teacher = Teacher.objects.create(user=user, name="Prof. Ana", school=self.school, specialty=specialty)
        self.academic_year = AcademicYear.objects.create(
            code="2026-2027",
            tenant_id=self.school.tenant_id,
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
            tenant_id=self.school.tenant_id,
            identification_document=SimpleUploadedFile("id.pdf", b"%PDF-1.4 test"),
            previous_certificate=SimpleUploadedFile("cert.pdf", b"%PDF-1.4 test"),
        )
        Enrollment.objects.create(student=self.student, classroom=self.classroom)
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
            cycle=1,
            subject=self.subject,
        )
        self.competencia_outra_disciplina = Competency.objects.create(
            name="Interpretar factos historicos",
            cycle=1,
            subject=self.outra_disciplina,
        )
