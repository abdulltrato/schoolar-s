from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Aluno


class AlunoModelTests(TestCase):
    def test_rejeita_classe_fora_do_intervalo(self):
        with self.assertRaises(ValidationError):
            Aluno.objects.create(
                nome="Aluno Inválido",
                data_nascimento=date(2015, 1, 1),
                classe=0,
                ciclo=1,
            )

    def test_define_ciclo_automaticamente_a_partir_da_classe(self):
        aluno = Aluno.objects.create(
            nome="Aluno Coerente",
            data_nascimento=date(2014, 1, 1),
            classe=5,
            ciclo=1,
        )

        self.assertEqual(aluno.ciclo, 2)

    def test_define_ensino_secundario_e_primeiro_ciclo_para_classe_7(self):
        aluno = Aluno.objects.create(
            nome="Aluno Secundario",
            data_nascimento=date(2012, 1, 1),
            classe=7,
            ciclo=1,
        )

        self.assertEqual(aluno.nivel_ensino, "secundario")
        self.assertEqual(aluno.ciclo, 1)
