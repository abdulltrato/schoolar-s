from datetime import date

from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.school.models import School
from .models import Student


class AlunoModelTests(TestCase):
    def test_rejeita_classe_fora_do_intervalo(self):
        with self.assertRaises(ValidationError):
            Student.objects.create(
                name="Student Inválido",
                birth_date=date(2015, 1, 1),
                grade=0,
                cycle=1,
                tenant_id="tenant-esc-1",
            )

    def test_define_ciclo_automaticamente_a_partir_da_classe(self):
        student = Student.objects.create(
            name="Student Coerente",
            birth_date=date(2014, 1, 1),
            grade=5,
            cycle=1,
            tenant_id="tenant-esc-1",
        )

        self.assertEqual(student.cycle, 2)

    def test_define_ensino_secundario_e_primeiro_ciclo_para_classe_7(self):
        student = Student.objects.create(
            name="Student Secundario",
            birth_date=date(2012, 1, 1),
            grade=7,
            cycle=1,
            tenant_id="tenant-esc-1",
        )

        self.assertEqual(student.education_level, "secundario")
        self.assertEqual(student.cycle, 1)


class AlunoAdminTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_superuser(
            username="admin-academic",
            email="admin@example.com",
            password="secret",
        )
        self.user.school_profile.role = "school_director"
        self.user.school_profile.tenant_id = "tenant-admin"
        self.user.school_profile.school = School.objects.create(
            code="ESC-ADM",
            name="Escola Admin",
            tenant_id="tenant-admin",
        )
        self.user.school_profile.save(update_fields=["role", "tenant_id", "school"])
        self.client.force_login(self.user)

    def test_admin_add_herda_tenant_do_perfil_autenticado(self):
        response = self.client.post(
            reverse("admin:academic_student_add"),
            {
                "name": "Aluno Admin",
                "birth_date": "2014-01-01",
                "grade": "5",
                "estado": "active",
                "_save": "Save",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        student = Student.objects.get(name="Aluno Admin")
        self.assertEqual(student.tenant_id, "tenant-admin")
        self.assertEqual(student.cycle, 2)

    def test_admin_add_sem_tenant_retorna_erro_de_formulario(self):
        self.user.school_profile.tenant_id = ""
        self.user.school_profile.school = None
        self.user.school_profile.save(update_fields=["tenant_id", "school"])

        response = self.client.post(
            reverse("admin:academic_student_add"),
            {
                "name": "Aluno Sem Tenant",
                "birth_date": "2014-01-01",
                "grade": "5",
                "estado": "active",
                "_save": "Save",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Student.objects.filter(name="Aluno Sem Tenant").exists())
        self.assertContains(response, "Tenant_id is required.")
