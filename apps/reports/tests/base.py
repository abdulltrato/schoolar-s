from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase

from apps.academic.models import Student
from apps.assessment.models import AssessmentPeriod, SubjectPeriodResult
from apps.curriculum.models import CurriculumArea, Subject, SubjectSpecialty
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


class ReportApiBase(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.tenant_id = "tenant-01"
        self.user = user_model.objects.create_user(username="director", password="secret123")
        self.teacher_user = user_model.objects.create_user(username="teacher", password="secret123")

        self.school = School.objects.create(code="ESC-01", name="Escola Primaria Central", tenant_id=self.tenant_id)
        area = CurriculumArea.objects.create(name="Ciencias")
        self.subject = Subject.objects.create(name="Matematica", area=area, cycle=1)
        specialty = SubjectSpecialty.objects.create(subject=self.subject, name="Matematica")
        self.academic_year = AcademicYear.objects.create(
            code="2026-2027",
            tenant_id=self.tenant_id,
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
            specialty=specialty,
        )
        self.classroom = Classroom.objects.create(
            name="2A",
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
            identification_document=SimpleUploadedFile("id-beto.pdf", b"%PDF-1.4 test"),
            previous_certificate=SimpleUploadedFile("cert-beto.pdf", b"%PDF-1.4 test"),
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            classroom=self.classroom,
        )

        self.profile: UserProfile = self.user.school_profile
        self.profile.role = "school_director"
        self.profile.school = self.school
        self.profile.tenant_id = self.tenant_id
        self.profile.active = True
        self.profile.save()

        self.grade_subject = GradeSubject.objects.create(
            academic_year=self.academic_year,
            grade=self.grade,
            subject=self.subject,
            weekly_workload=5,
        )
        self.assignment = TeachingAssignment.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
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
