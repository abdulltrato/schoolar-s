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

    def test_rejeita_ciclo_incompativel_com_classe(self):
        with self.assertRaises(ValidationError):
            Aluno.objects.create(
                nome="Aluno Incoerente",
                data_nascimento=date(2014, 1, 1),
                classe=5,
                ciclo=1,
            )
