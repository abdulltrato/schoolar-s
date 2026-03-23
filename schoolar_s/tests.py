from django.test import TestCase
from django.test.utils import override_settings
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.school.models import AuditAlert, AuditEvent, UserProfile, School


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


class AuthContractTests(TestCase):
    def test_login_retorna_perfil_sincronizado(self):
        user = get_user_model().objects.create_user(username="login-user", password="secret")
        profile = user.school_profile
        profile.role = "finance_officer"
        profile.tenant_id = "tenant-auth"
        profile.save(update_fields=["role", "tenant_id"])

        response = self.client.post(
            "/api/v1/auth/login/",
            {"username": "login-user", "password": "secret"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["ok"])
        self.assertEqual(response.json()["user"]["role"], "finance_officer")
        self.assertEqual(response.json()["user"]["tenant_id"], "tenant-auth")

    @override_settings(REQUIRE_USER_PROFILE=True)
    def test_me_exige_sessao(self):
        response = self.client.get("/api/v1/auth/me/")

        self.assertEqual(response.status_code, 401)
        self.assertFalse(response.json()["ok"])

    @override_settings(REQUIRE_USER_PROFILE=True)
    def test_api_negada_sem_user_profile_quando_exigido(self):
        user = get_user_model().objects.create_user(username="sem-perfil", password="secret")
        UserProfile.objects.filter(user=user).delete()
        user = get_user_model().objects.get(pk=user.pk)
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/v1/academic/alunos/")

        self.assertEqual(response.status_code, 403)
        self.assertFalse(response.json()["ok"])


class AuditContractTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="audit-user", password="secret")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_announcement_create_emits_audit_log(self):
        school = School.objects.create(code="AUD-01", name="Audit School")

        with self.assertLogs("schoolar.audit", level="INFO") as captured:
            response = self.client.post(
                "/api/v1/school/announcements/",
                {
                    "school": school.id,
                    "title": "Manutencao",
                    "message": "Sistema em manutencao.",
                    "audience": "school",
                },
                format="json",
            )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(any("resource_mutation" in entry for entry in captured.output))
        event = AuditEvent.objects.get(resource="announcement", action="create")
        self.assertEqual(event.object_id, response.json()["id"])
        self.assertEqual(event.username, "audit-user")

    def test_announcement_update_emits_audit_log(self):
        school = School.objects.create(code="AUD-02", name="Audit School 2")
        create_response = self.client.post(
            "/api/v1/school/announcements/",
            {
                "school": school.id,
                "title": "Aviso de prova",
                "message": "A prova sera reagendada.",
                "audience": "school",
            },
            format="json",
        )
        announcement_id = create_response.json()["id"]

        with self.assertLogs("schoolar.audit", level="INFO") as captured:
            response = self.client.patch(
                f"/api/v1/school/announcements/{announcement_id}/",
                {
                    "active": False,
                    "message": "A prova foi reagendada para sexta.",
                },
                format="json",
            )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(any("resource_mutation" in entry for entry in captured.output))
        event = AuditEvent.objects.filter(resource="announcement", action="update").latest("created_at")
        self.assertIn("active", event.changed_fields)
        self.assertIn("message", event.changed_fields)

    def test_audit_api_filters_by_resource(self):
        school = School.objects.create(code="AUD-03", name="Audit School 3")
        self.client.post(
            "/api/v1/school/announcements/",
            {
                "school": school.id,
                "title": "Filtro",
                "message": "Evento filtravel.",
                "audience": "school",
            },
            format="json",
        )

        response = self.client.get("/api/v1/school/audit-events/?resource=announcement")

        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.json()["count"], 1)
        self.assertTrue(all(item["resource"] == "announcement" for item in response.json()["results"]))

    def test_audit_export_csv_returns_attachment(self):
        school = School.objects.create(code="AUD-04", name="Audit School 4")
        self.client.post(
            "/api/v1/school/announcements/",
            {
                "school": school.id,
                "title": "Export",
                "message": "Evento exportavel.",
                "audience": "school",
            },
            format="json",
        )

        response = self.client.get("/api/v1/school/audit-events/exports/download/?resource=announcement&export_format=csv")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn("attachment;", response["Content-Disposition"])

    def test_repeated_audit_events_generate_alert(self):
        school = School.objects.create(code="AUD-05", name="Audit School 5")

        for index in range(5):
            self.client.post(
                "/api/v1/school/announcements/",
                {
                    "school": school.id,
                    "title": f"Alerta {index}",
                    "message": "Evento para gatilhar alerta.",
                    "audience": "school",
                },
                format="json",
            )

        self.assertTrue(AuditAlert.objects.filter(alert_type="actor_concentration", username="audit-user").exists())

    def test_audit_alert_api_filters_and_acknowledges_alert(self):
        alert = AuditAlert.objects.create(
            alert_type="high_recent_volume",
            severity="elevated",
            tenant_id="tenant-audit",
            resource="announcement",
            username="audit-user",
            summary="High volume detected.",
            acknowledged=False,
        )
        AuditAlert.objects.create(
            alert_type="resource_concentration",
            severity="watch",
            tenant_id="tenant-other",
            resource="invoice",
            username="other-user",
            summary="Other alert.",
            acknowledged=True,
        )

        filter_response = self.client.get(
            "/api/v1/school/audit-alerts/?severity=elevated&acknowledged=false&resource=announcement&tenant_id=tenant-audit"
        )

        self.assertEqual(filter_response.status_code, 200)
        self.assertEqual(filter_response.json()["count"], 1)
        self.assertEqual(filter_response.json()["results"][0]["id"], alert.id)

        acknowledge_response = self.client.post(f"/api/v1/school/audit-alerts/{alert.id}/acknowledge/")

        self.assertEqual(acknowledge_response.status_code, 200)
        alert.refresh_from_db()
        self.assertTrue(alert.acknowledged)
