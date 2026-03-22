from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from aplicativos.academico.models import Aluno
from .models import Professor, Turma, Matricula


class EscolaModelTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username="prof", password="secret")
        self.professor = Professor.objects.create(user=user, nome="Prof. Carla")
        self.aluno = Aluno.objects.create(
            nome="Beto",
            data_nascimento=date(2015, 5, 20),
            classe=2,
            ciclo=1,
        )

    def test_rejeita_turma_com_ano_letivo_invalido(self):
        with self.assertRaises(ValidationError):
            Turma.objects.create(
                nome="Turma A",
                ciclo=1,
                ano_letivo="2026",
                professor_responsavel=self.professor,
            )

    def test_rejeita_matricula_com_ciclo_diferente(self):
        turma = Turma.objects.create(
            nome="Turma B",
            ciclo=2,
            ano_letivo="2026-2027",
            professor_responsavel=self.professor,
        )

        with self.assertRaises(ValidationError):
            Matricula.objects.create(aluno=self.aluno, turma=turma)
