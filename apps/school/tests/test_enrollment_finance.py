from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from apps.academic.models import Student
from apps.curriculum.models import CurriculumArea, Subject, SubjectSpecialty
from apps.school.models import (
    AcademicYear,
    Classroom,
    Enrollment,
    Grade,
    Invoice,
    PaymentPlan,
    School,
    Teacher,
)


class EnrollmentFinanceTests(TestCase):
    def _doc(self, name="doc.pdf"):
        return SimpleUploadedFile(name, b"%PDF-1.4 test doc")

    def setUp(self):
        self.school = School.objects.create(
            code="ESC-02",
            name="School Finance Test",
            tenant_id="tenant-finance-01",
        )
        self.academic_year = AcademicYear.objects.create(
            code="2026-2027",
            tenant_id=self.school.tenant_id,
            start_date=date(2026, 2, 1),
            end_date=date(2026, 12, 15),
            active=True,
        )
        self.grade = Grade.objects.create(number=2, cycle=1)
        area = CurriculumArea.objects.create(name="Ciencias", tenant_id=self.school.tenant_id)
        subject = Subject.objects.create(
            name="Matematica",
            area=area,
            cycle=1,
            tenant_id=self.school.tenant_id,
        )
        specialty = SubjectSpecialty.objects.create(
            subject=subject,
            name="Matematica",
        )
        user = get_user_model().objects.create_user(username="finance-prof", password="secret")
        self.teacher = Teacher.objects.create(
            user=user,
            name="Prof Finance",
            school=self.school,
            specialty=specialty,
            tenant_id=self.school.tenant_id,
        )
        self.classroom = Classroom.objects.create(
            name="Finance Classroom",
            school=self.school,
            grade=self.grade,
            cycle=1,
            academic_year=self.academic_year,
            lead_teacher=self.teacher,
        )
        self.student = Student.objects.create(
            name="Finance Student",
            birth_date=date(2015, 5, 20),
            grade=2,
            cycle=1,
            tenant_id=self.school.tenant_id,
            identification_document=self._doc("id-finance.pdf"),
            previous_certificate=self._doc("cert-finance.pdf"),
        )

    def test_enrollment_generates_invoice_and_payment_plans(self):
        enrollment = Enrollment.objects.create(
            student=self.student,
            classroom=self.classroom,
            enrollment_fee=Decimal("200"),
            monthly_fee=Decimal("150"),
            monthly_fee_start=date(2026, 2, 1),
            monthly_fee_end=date(2026, 4, 30),
            exam_fee=Decimal("0"),
        )

        draft_invoices = Invoice.objects.filter(student=self.student, status="draft")
        self.assertEqual(draft_invoices.count(), 1)
        enrollment_plan = PaymentPlan.objects.get(
            enrollment=enrollment,
            type="enrollment_fee",
        )
        self.assertEqual(enrollment_plan.amount, Decimal("200"))
        self.assertIsNotNone(enrollment_plan.invoice)
        self.assertEqual(enrollment_plan.invoice.reference, f"MAT-{enrollment.code}")

        tuition_plans = PaymentPlan.objects.filter(enrollment=enrollment, type="tuition_monthly").order_by("due_date")
        self.assertEqual(tuition_plans.count(), 3)
        expected_dues = [date(2026, 2, 1), date(2026, 3, 1), date(2026, 4, 1)]
        self.assertEqual([plan.due_date for plan in tuition_plans], expected_dues)
        self.assertTrue(all(plan.status == "scheduled" for plan in tuition_plans))

        propina_plan = PaymentPlan.objects.get(enrollment=enrollment, type="propina")
        self.assertEqual(propina_plan.amount, Decimal("150"))
        self.assertEqual(propina_plan.due_date, self.academic_year.start_date)

        exam_plans = PaymentPlan.objects.filter(enrollment=enrollment, type__startswith="exam")
        self.assertEqual(exam_plans.count(), 0)
