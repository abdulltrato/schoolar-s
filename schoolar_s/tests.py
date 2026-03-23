from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


class HealthcheckTests(TestCase):
    def test_healthcheck_retorna_status_ok(self):
        response = self.client.get("/health/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_healthcheck_retorna_request_id_no_header(self):
        response = self.client.get("/health/", HTTP_X_REQUEST_ID="req-123")

        self.assertEqual(response["X-Request-ID"], "req-123")

    def test_readiness_retorna_ok(self):
        response = self.client.get("/ready/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["checks"]["database"], "ok")
        self.assertEqual(response.json()["checks"]["cache"], "ok")


class ErrorContractTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="apiuser", password="secret")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_erros_da_api_seguem_envelope_padrao(self):
        response = self.client.post(
            "/api/v1/academic/alunos/",
            {
                "name": "Student",
                "birth_date": "2016-01-01",
                "grade": 5,
                "cycle": 1,
                "estado": "active",
            },
            format="json",
            HTTP_X_REQUEST_ID="req-error-1",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["ok"])
        self.assertEqual(response.json()["meta"]["request_id"], "req-error-1")
        self.assertIn("error", response.json())
