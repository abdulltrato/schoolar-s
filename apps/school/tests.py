from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework.test import APIClient

from apps.academic.models import Student
from apps.curriculum.models import CurriculumArea, Subject, SubjectSpecialty
from .models import (
    TeachingAssignment,
    AcademicYear,
    ManagementAssignment,
    Grade,
    GradeSubject,
    School,
    Enrollment,
    Teacher,
    Classroom,
)


class EscolaModelTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(code="ESC-01", name="School Primaria Central", tenant_id="tenant-esc-01")
        area = CurriculumArea.objects.create(name="Ciencias")
        subject = Subject.objects.create(name="Matematica", area=area, cycle=1)
        specialty = SubjectSpecialty.objects.create(subject=subject, name="Matematica")
        user = get_user_model().objects.create_user(username="prof", password="secret")
        self.teacher = Teacher.objects.create(user=user, name="Prof. Carla", school=self.school, specialty_subject=specialty)
        self.student = Student.objects.create(
            name="Beto",
            birth_date=date(2015, 5, 20),
            grade=2,
            cycle=1,
            tenant_id=self.school.tenant_id,
        )
        self.academic_year = AcademicYear.objects.create(
            code="2026-2027",
            tenant_id=self.school.tenant_id,
            start_date=date(2026, 2, 1),
            end_date=date(2026, 12, 15),
            active=True,
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
        self.subject = subject

    def test_rejeita_ano_letivo_com_codigo_invalido(self):
        with self.assertRaises(ValidationError):
            AcademicYear.objects.create(
                code="2026",
                tenant_id=self.school.tenant_id,
                start_date=date(2026, 2, 1),
                end_date=date(2026, 12, 15),
            )

    def test_rejeita_disciplina_classe_de_ciclo_diferente(self):
        classe_ciclo_2 = Grade.objects.create(number=4, cycle=2)

        with self.assertRaises(ValidationError):
            GradeSubject.objects.create(
                academic_year=self.academic_year,
                grade=classe_ciclo_2,
                subject=self.subject,
            )

    def test_rejeita_alocacao_docente_com_classe_diferente_da_turma(self):
        grade_subject = GradeSubject.objects.create(
            academic_year=self.academic_year,
            grade=self.grade,
            subject=self.subject,
        )
        outra_classe = Grade.objects.create(number=1, cycle=1)
        outra_turma = Classroom.objects.create(
            name="Classroom B",
            school=self.school,
            grade=outra_classe,
            cycle=1,
            academic_year=self.academic_year,
            lead_teacher=self.teacher,
        )

        with self.assertRaises(ValidationError):
            TeachingAssignment.objects.create(
                teacher=self.teacher,
                classroom=outra_turma,
                grade_subject=grade_subject,
            )

    def test_rejeita_matricula_com_classe_diferente(self):
        turma_outra_classe = Classroom.objects.create(
            name="Classroom C",
            school=self.school,
            grade=Grade.objects.create(number=3, cycle=1),
            cycle=1,
            academic_year=self.academic_year,
            lead_teacher=self.teacher,
        )

        with self.assertRaises(ValidationError):
            Enrollment.objects.create(student=self.student, classroom=turma_outra_classe)

    def test_rejeita_director_de_turma_sem_turma(self):
        with self.assertRaises(ValidationError):
            ManagementAssignment.objects.create(
                teacher=self.teacher,
                school=self.school,
                academic_year=self.academic_year,
                role="director_turma",
            )

    def test_cria_coordenador_de_classe_com_escopo_valido(self):
        atribuicao = ManagementAssignment.objects.create(
            teacher=self.teacher,
            school=self.school,
            academic_year=self.academic_year,
            role="coordenador_classe",
            grade=self.grade,
        )

        self.assertEqual(atribuicao.grade, self.grade)

    def test_define_secundario_e_ciclo_1_para_classe_7(self):
        grade = Grade.objects.create(number=7, cycle=1)

        self.assertEqual(grade.education_level, "secundario")
        self.assertEqual(grade.cycle, 1)


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
            specialty_subject=specialty,
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
        )

        user.refresh_from_db()
        self.assertEqual(user.school_profile.role, "student")
        self.assertEqual(user.school_profile.tenant_id, "tenant-student")


class TeacherUsuarioApiTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_user(username="admin-teacher-usuario", password="secret")
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)
        self.tenant_id = "tenant-teacher-usuario"
        self.school = School.objects.create(
            code="ESC-TU-01",
            name="Escola Teacher Usuario",
            tenant_id=self.tenant_id,
        )
        area = CurriculumArea.objects.create(name="Area TU")
        subject = Subject.objects.create(name="Matematica", area=area, cycle=1)
        self.specialty = SubjectSpecialty.objects.create(subject=subject, name="Matematica")
        self.teacher_user = get_user_model().objects.create_user(username="teacher-usuario", password="secret")

    def test_teacher_usuario_readonly_e_auto(self):
        payload = {
            "user": self.teacher_user.id,
            "school": self.school.id,
            "name": "Professor Usuario",
            "specialty_subject": self.specialty.id,
            "usuario": self.teacher_user.id,
        }
        response = self.client.post(
            "/api/v1/school/teachers/",
            payload,
            format="json",
            HTTP_X_TENANT_ID=self.tenant_id,
        )
        self.assertEqual(response.status_code, 400)
        error_details = (response.json().get("error") or {}).get("details") or {}
        self.assertIn("usuario", error_details)

        payload.pop("usuario", None)
        response = self.client.post(
            "/api/v1/school/teachers/",
            payload,
            format="json",
            HTTP_X_TENANT_ID=self.tenant_id,
        )
        self.assertEqual(response.status_code, 201)
        body = response.json()
        if isinstance(body, dict) and "data" in body and (body.get("ok") is True or body.get("ok") is False):
            body = body.get("data") or {}
        self.assertEqual(body.get("usuario"), self.admin.id)
