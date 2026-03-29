from datetime import date

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from apps.academic.models import Student
from apps.curriculum.models import CurriculumArea, Subject, SubjectSpecialty
from apps.school.models import School, Teacher


class UserProfileSignalTests(TestCase):
    def test_cria_perfil_padrao_quando_utilizador_e_criado(self):
        user = get_user_model().objects.create_user(username="novo", password="secret")

        self.assertTrue(hasattr(user, "school_profile"))
        self.assertEqual(user.school_profile.role, "national_admin")
        self.assertTrue(user.school_profile.active)

    def test_sincroniza_perfil_para_professor(self):
        school = School.objects.create(
            code="ESC-02",
            name="Escola Secundaria Central",
            province="Maputo",
            district="KaMpfumo",
            tenant_id="tenant-school-02",
        )
        area = CurriculumArea.objects.create(name="Area Prof")
        subject = Subject.objects.create(name="Matematica", area=area, cycle=1)
        specialty = SubjectSpecialty.objects.create(subject=subject, name="Matematica")
        user = get_user_model().objects.create_user(username="teacher-sync", password="secret")

        Teacher.objects.create(
            user=user,
            name="Prof. Joao",
            school=school,
            specialty=specialty,
            tenant_id="tenant-school-02",
        )

        user.refresh_from_db()
        self.assertEqual(user.school_profile.role, "teacher")
        self.assertEqual(user.school_profile.tenant_id, "tenant-school-02")
        self.assertEqual(user.school_profile.school, school)
        self.assertEqual(user.school_profile.province, "Maputo")
        self.assertEqual(user.school_profile.district, "KaMpfumo")

    def test_sincroniza_perfil_para_aluno(self):
        user = get_user_model().objects.create_user(username="student-sync", password="secret")

        Student.objects.create(
            user=user,
            name="Aluno Portal",
            birth_date=date(2014, 1, 1),
            grade=6,
            cycle=1,
            tenant_id="tenant-student",
            identification_document=SimpleUploadedFile("id-portal.pdf", b"%PDF-1.4 test"),
            previous_certificate=SimpleUploadedFile("cert-portal.pdf", b"%PDF-1.4 test"),
        )

        user.refresh_from_db()
        self.assertEqual(user.school_profile.role, "student")
        self.assertEqual(user.school_profile.tenant_id, "tenant-student")
