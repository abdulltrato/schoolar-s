from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Event


class EventoTenantApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="tenant-user", password="secret")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_forca_tenant_do_header(self):
        response = self.client.post(
            "/api/v1/events/events/",
            {
                "tipo": "aluno_registrado",
                "dados": {"aluno_id": 1},
                "tenant_id": "payload-invalido",
            },
            format="json",
            HTTP_X_TENANT_ID="school-secundaria",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["tenant_id"], "school-secundaria")

    def test_list_filtra_por_tenant_header(self):
        Event.objects.create(tipo="aluno_registrado", dados={"aluno_id": 1}, tenant_id="school-a")
        Event.objects.create(tipo="aluno_registrado", dados={"aluno_id": 2}, tenant_id="school-b")

        response = self.client.get("/api/v1/events/events/", HTTP_X_TENANT_ID="school-a")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["tenant_id"], "school-a")
