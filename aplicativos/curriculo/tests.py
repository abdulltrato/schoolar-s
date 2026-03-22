from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework.test import APIClient

from aplicativos.escola.models import AnoLetivo, Classe, DisciplinaClasse
from .models import AreaCurricular, Competencia, CurriculoBase, Disciplina, PlanoCurricularDisciplina


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

    def test_cria_plano_curricular_para_disciplina_da_classe(self):
        area = AreaCurricular.objects.create(nome="Ciências Exatas")
        disciplina = Disciplina.objects.create(nome="Matemática", area=area, ciclo=1)
        ano_letivo = AnoLetivo.objects.create(
            codigo="2026-2027",
            data_inicio=date(2026, 2, 1),
            data_fim=date(2026, 12, 15),
            ativo=True,
        )
        classe = Classe.objects.create(numero=2, ciclo=1)
        disciplina_classe = DisciplinaClasse.objects.create(
            ano_letivo=ano_letivo,
            classe=classe,
            disciplina=disciplina,
        )

        plano = PlanoCurricularDisciplina.objects.create(
            disciplina_classe=disciplina_classe,
            objetivos="Consolidar operacoes basicas.",
            metodologia="Aulas praticas e resolucao de problemas.",
        )

        self.assertEqual(plano.disciplina_classe, disciplina_classe)

    def test_rejeita_competencia_de_outra_disciplina_no_plano(self):
        area = AreaCurricular.objects.create(nome="Ciências Integradas")
        disciplina = Disciplina.objects.create(nome="Matemática", area=area, ciclo=1)
        outra_disciplina = Disciplina.objects.create(nome="História", area=area, ciclo=1)
        ano_letivo = AnoLetivo.objects.create(
            codigo="2027-2028",
            data_inicio=date(2027, 2, 1),
            data_fim=date(2027, 12, 15),
            ativo=True,
        )
        classe = Classe.objects.create(numero=3, ciclo=1)
        disciplina_classe = DisciplinaClasse.objects.create(
            ano_letivo=ano_letivo,
            classe=classe,
            disciplina=disciplina,
        )
        plano = PlanoCurricularDisciplina.objects.create(disciplina_classe=disciplina_classe)
        competencia_invalida = Competencia.objects.create(
            nome="Interpretar contextos históricos",
            area="linguagem_comunicacao",
            ciclo=1,
            disciplina=outra_disciplina,
        )

        with self.assertRaises(ValidationError):
            plano.competencias_previstas.add(competencia_invalida)
