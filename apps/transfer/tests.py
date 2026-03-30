from datetime import date
# Datas para anos letivos.

from django.contrib.auth import get_user_model
# Helper para modelo de usuário.
from django.test import TestCase
# Base de testes do Django.
from rest_framework.test import APIClient
# Cliente DRF para testes de API.

from apps.academic.models import Student
from apps.curriculum.models import CurriculumArea, Subject, SubjectSpecialty
from apps.school.models import AcademicYear, Classroom, Enrollment, Grade, GradeSubject, School, Teacher, TeachingAssignment


class TransferApiTests(TestCase):
    """Testes de API cobrindo fluxos de transferência de alunos e professores."""

    def setUp(self):
        self.admin = get_user_model().objects.create_user(username="admin-transfer", password="secret")
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

        self.school_a = School.objects.create(code="ESC-A", name="Escola A", tenant_id="tenant-a")
        self.school_b = School.objects.create(code="ESC-B", name="Escola B", tenant_id="tenant-b")

        self.grade2 = Grade.objects.create(number=2, cycle=1)

        self.year_a = AcademicYear.objects.create(
            code="2026-2027",
            tenant_id=self.school_a.tenant_id,
            start_date=date(2026, 2, 1),
            end_date=date(2026, 12, 15),
            active=True,
        )
        self.year_b = AcademicYear.objects.create(
            code="2026-2027",
            tenant_id=self.school_b.tenant_id,
            start_date=date(2026, 2, 1),
            end_date=date(2026, 12, 15),
            active=True,
        )

        self.class_a1 = Classroom.objects.create(
            name="Turma A1",
            school=self.school_a,
            grade=self.grade2,
            cycle=1,
            academic_year=self.year_a,
        )
        self.class_a2 = Classroom.objects.create(
            name="Turma A2",
            school=self.school_a,
            grade=self.grade2,
            cycle=1,
            academic_year=self.year_a,
        )
        self.class_b1 = Classroom.objects.create(
            name="Turma B1",
            school=self.school_b,
            grade=self.grade2,
            cycle=1,
            academic_year=self.year_b,
        )

    def _unwrap(self, response):
        body = response.json()
        if isinstance(body, dict) and "data" in body and ("ok" in body):
            return body.get("data") or {}
        return body

    def test_transfer_student_within_tenant_moves_enrollment(self):
        student = Student.objects.create(
            name="Aluno A",
            birth_date=date(2016, 1, 1),
            grade=2,
            cycle=1,
            tenant_id=self.school_a.tenant_id,
        )
        Enrollment.objects.create(student=student, classroom=self.class_a1)

        create_payload = {
            "kind": "student",
            "student": student.id,
            "from_classroom": self.class_a1.id,
            "to_classroom": self.class_a2.id,
            "reason": "Mudança de turma",
        }
        resp = self.client.post("/api/v1/transfer/transfers/", create_payload, format="json")
        self.assertEqual(resp.status_code, 201, resp.json())
        transfer_id = self._unwrap(resp).get("id")
        self.assertIsNotNone(transfer_id)

        apply_resp = self.client.post(f"/api/v1/transfer/transfers/{transfer_id}/apply/", {}, format="json")
        self.assertEqual(apply_resp.status_code, 200)

        active_enrollments = Enrollment.objects.filter(student=student, deleted_at__isnull=True).select_related("classroom")
        self.assertEqual(active_enrollments.count(), 1)
        self.assertEqual(active_enrollments.first().classroom_id, self.class_a2.id)

    def test_transfer_student_across_tenant_clones_student_and_moves_user(self):
        user = get_user_model().objects.create_user(username="student-x", password="secret")
        student = Student.objects.create(
            user=user,
            name="Aluno X",
            birth_date=date(2016, 5, 1),
            grade=2,
            cycle=1,
            tenant_id=self.school_a.tenant_id,
        )
        Enrollment.objects.create(student=student, classroom=self.class_a1)

        create_payload = {
            "kind": "student",
            "student": student.id,
            "from_classroom": self.class_a1.id,
            "to_classroom": self.class_b1.id,
            "reason": "Transferência de escola/tenant",
        }
        resp = self.client.post("/api/v1/transfer/transfers/", create_payload, format="json")
        self.assertEqual(resp.status_code, 201, resp.json())
        transfer_id = self._unwrap(resp).get("id")

        apply_resp = self.client.post(f"/api/v1/transfer/transfers/{transfer_id}/apply/", {}, format="json")
        self.assertEqual(apply_resp.status_code, 200)

        student.refresh_from_db()
        self.assertIsNone(student.user_id)
        self.assertEqual(student.tenant_id, "tenant-a")
        self.assertEqual(student.estado, "transferido")

        new_student = Student.objects.filter(user=user, tenant_id="tenant-b").first()
        self.assertIsNotNone(new_student)
        self.assertEqual(new_student.name, "Aluno X")

        self.assertTrue(hasattr(user, "school_profile"))
        user.refresh_from_db()
        self.assertEqual(user.school_profile.tenant_id, "tenant-b")
        self.assertEqual(user.school_profile.school_id, self.school_b.id)

        self.assertTrue(
            Enrollment.objects.filter(student=new_student, classroom=self.class_b1, deleted_at__isnull=True).exists()
        )

    def test_transfer_teacher_across_tenant_moves_teacher_and_detaches_old_relations(self):
        # specialty in tenant A
        area_a = CurriculumArea.objects.create(name="Area A", tenant_id="tenant-a")
        subj_a = Subject.objects.create(name="Mat A", area=area_a, cycle=1)
        spec_a = SubjectSpecialty.objects.create(subject=subj_a, name="Mat A")

        # specialty in tenant B
        area_b = CurriculumArea.objects.create(name="Area B", tenant_id="tenant-b")
        subj_b = Subject.objects.create(name="Mat B", area=area_b, cycle=1)
        spec_b = SubjectSpecialty.objects.create(subject=subj_b, name="Mat B")

        teacher_user = get_user_model().objects.create_user(username="teacher-x", password="secret")
        teacher = Teacher.objects.create(
            user=teacher_user,
            name="Professor X",
            school=self.school_a,
            specialty=spec_a,
            tenant_id="tenant-a",
        )
        self.class_a1.lead_teacher = teacher
        self.class_a1.save()

        grade_subject = GradeSubject.objects.create(
            academic_year=self.year_a,
            grade=self.grade2,
            subject=subj_a,
            tenant_id="tenant-a",
        )
        assignment = TeachingAssignment.objects.create(
            teacher=teacher,
            classroom=self.class_a1,
            grade_subject=grade_subject,
            tenant_id="tenant-a",
        )

        create_payload = {
            "kind": "teacher",
            "teacher": teacher.id,
            "to_school": self.school_b.id,
            "new_specialty": spec_b.id,
            "reason": "Transferência de professor",
        }
        resp = self.client.post("/api/v1/transfer/transfers/", create_payload, format="json")
        self.assertEqual(resp.status_code, 201, resp.json())
        transfer_id = self._unwrap(resp).get("id")

        apply_resp = self.client.post(f"/api/v1/transfer/transfers/{transfer_id}/apply/", {}, format="json")
        self.assertEqual(apply_resp.status_code, 200)

        teacher.refresh_from_db()
        self.assertEqual(teacher.tenant_id, "tenant-b")
        self.assertEqual(teacher.school_id, self.school_b.id)
        self.assertEqual(teacher.specialty_id, spec_b.id)

        self.class_a1.refresh_from_db()
        self.assertIsNone(self.class_a1.lead_teacher_id)

        assignment.refresh_from_db()
        self.assertIsNotNone(assignment.deleted_at)
