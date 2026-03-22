from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .models import AreaCurricular, CurriculoBase, Disciplina


class CurriculoApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="admin", password="secret")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_cria_disciplina_usando_area_id(self):
        area = AreaCurricular.objects.create(nome="Ciências")

        response = self.client.post(
            "/api/v1/curriculo/disciplinas/",
            {"nome": "Matemática", "area_id": area.id, "ciclo": 1},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        disciplina = Disciplina.objects.get(nome="Matemática")
        self.assertEqual(disciplina.area, area)

    def test_cria_curriculo_base_usando_lista_de_competencias(self):
        area = AreaCurricular.objects.create(nome="Comunicação")
        disciplina = Disciplina.objects.create(nome="Português", area=area, ciclo=1)
        competencia = disciplina.competencia_set.create(
            nome="Ler textos curtos",
            area="linguagem_comunicacao",
            ciclo=1,
        )

        response = self.client.post(
            "/api/v1/curriculo/curriculos-base/",
            {"ciclo": 1, "competencia_ids": [competencia.id]},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        curriculo = CurriculoBase.objects.get(pk=response.data["id"])
        self.assertEqual(list(curriculo.competencias.all()), [competencia])

    def test_curriculo_local_respeita_tenant_do_header(self):
        response = self.client.post(
            "/api/v1/curriculo/curriculos-local/",
            {"tenant_id": "payload-a", "ciclo": 1},
            format="json",
            HTTP_X_TENANT_ID="escola-central",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["tenant_id"], "escola-central")
