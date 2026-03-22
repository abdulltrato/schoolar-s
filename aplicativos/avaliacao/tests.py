from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from aplicativos.academico.models import Aluno
from aplicativos.curriculo.models import AreaCurricular, Disciplina, Competencia
from .models import Avaliacao


class AvaliacaoModelTests(TestCase):
    def setUp(self):
        area = AreaCurricular.objects.create(nome="Ciências Naturais")
        disciplina_ciclo_1 = Disciplina.objects.create(nome="Matemática", area=area, ciclo=1)
        disciplina_ciclo_2 = Disciplina.objects.create(nome="Física", area=area, ciclo=2)
        self.competencia_ciclo_1 = Competencia.objects.create(
            nome="Resolver operações básicas",
            area="saber_cientifico_tecnologico",
            ciclo=1,
            disciplina=disciplina_ciclo_1,
        )
        self.competencia_ciclo_2 = Competencia.objects.create(
            nome="Resolver problemas avançados",
            area="saber_cientifico_tecnologico",
            ciclo=2,
            disciplina=disciplina_ciclo_2,
        )
        self.aluno_ciclo_1 = Aluno.objects.create(
            nome="Ana",
            data_nascimento=date(2016, 2, 1),
            classe=2,
            ciclo=1,
        )

    def test_rejeita_avaliacao_sem_eixos_marcados(self):
        with self.assertRaises(ValidationError):
            Avaliacao.objects.create(
                aluno=self.aluno_ciclo_1,
                competencia=self.competencia_ciclo_1,
                tipo="formativa",
                data=date(2026, 3, 1),
            )

    def test_rejeita_avaliacao_com_ciclos_diferentes(self):
        with self.assertRaises(ValidationError):
            Avaliacao.objects.create(
                aluno=self.aluno_ciclo_1,
                competencia=self.competencia_ciclo_2,
                tipo="formativa",
                data=date(2026, 3, 1),
                conhecimentos=True,
            )
