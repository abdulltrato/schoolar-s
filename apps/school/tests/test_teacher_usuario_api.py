from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.curriculum.models import CurriculumArea, Subject, SubjectSpecialty
from apps.school.models import School


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
            "specialty": self.specialty.id,
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
