from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from aplicativos.academico.models import Aluno
from .models import Relatorio


class RelatorioModelTests(TestCase):
    def setUp(self):
        self.aluno = Aluno.objects.create(
            nome="Lina",
            data_nascimento=date(2015, 3, 12),
            classe=1,
            ciclo=1,
        )

    def test_relatorio_de_aluno_exige_aluno(self):
        with self.assertRaises(ValidationError):
            Relatorio.objects.create(
                titulo="Relatório sem aluno",
                tipo="aluno",
                periodo="2026-2027",
                conteudo={"total": 1},
            )

    def test_relatorio_de_escola_nao_aceita_aluno(self):
        with self.assertRaises(ValidationError):
            Relatorio.objects.create(
                titulo="Relatório de escola",
                tipo="escola",
                periodo="2026-2027",
                conteudo={"total": 1},
                aluno=self.aluno,
            )
