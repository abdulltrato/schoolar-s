from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from aplicativos.academico.models import Aluno
from aplicativos.curriculo.models import AreaCurricular, Disciplina
from .models import AlocacaoDocente, AnoLetivo, AtribuicaoGestao, Classe, DisciplinaClasse, Escola, Matricula, Professor, Turma


class EscolaModelTests(TestCase):
    def setUp(self):
        self.escola = Escola.objects.create(codigo="ESC-01", nome="Escola Primaria Central")
        user = get_user_model().objects.create_user(username="prof", password="secret")
        self.professor = Professor.objects.create(user=user, nome="Prof. Carla", escola=self.escola)
        self.aluno = Aluno.objects.create(
            nome="Beto",
            data_nascimento=date(2015, 5, 20),
            classe=2,
            ciclo=1,
        )
        self.ano_letivo = AnoLetivo.objects.create(
            codigo="2026-2027",
            data_inicio=date(2026, 2, 1),
            data_fim=date(2026, 12, 15),
            ativo=True,
        )
        self.classe = Classe.objects.create(numero=2, ciclo=1)
        self.turma = Turma.objects.create(
            nome="Turma A",
            escola=self.escola,
            classe=self.classe,
            ciclo=1,
            ano_letivo=self.ano_letivo,
            professor_responsavel=self.professor,
        )
        area = AreaCurricular.objects.create(nome="Ciencias")
        self.disciplina = Disciplina.objects.create(nome="Matematica", area=area, ciclo=1)

    def test_rejeita_ano_letivo_com_codigo_invalido(self):
        with self.assertRaises(ValidationError):
            AnoLetivo.objects.create(
                codigo="2026",
                data_inicio=date(2026, 2, 1),
                data_fim=date(2026, 12, 15),
            )

    def test_rejeita_disciplina_classe_de_ciclo_diferente(self):
        classe_ciclo_2 = Classe.objects.create(numero=4, ciclo=2)

        with self.assertRaises(ValidationError):
            DisciplinaClasse.objects.create(
                ano_letivo=self.ano_letivo,
                classe=classe_ciclo_2,
                disciplina=self.disciplina,
            )

    def test_rejeita_alocacao_docente_com_classe_diferente_da_turma(self):
        disciplina_classe = DisciplinaClasse.objects.create(
            ano_letivo=self.ano_letivo,
            classe=self.classe,
            disciplina=self.disciplina,
        )
        outra_classe = Classe.objects.create(numero=1, ciclo=1)
        outra_turma = Turma.objects.create(
            nome="Turma B",
            escola=self.escola,
            classe=outra_classe,
            ciclo=1,
            ano_letivo=self.ano_letivo,
            professor_responsavel=self.professor,
        )

        with self.assertRaises(ValidationError):
            AlocacaoDocente.objects.create(
                professor=self.professor,
                turma=outra_turma,
                disciplina_classe=disciplina_classe,
            )

    def test_rejeita_matricula_com_classe_diferente(self):
        turma_outra_classe = Turma.objects.create(
            nome="Turma C",
            escola=self.escola,
            classe=Classe.objects.create(numero=3, ciclo=1),
            ciclo=1,
            ano_letivo=self.ano_letivo,
            professor_responsavel=self.professor,
        )

        with self.assertRaises(ValidationError):
            Matricula.objects.create(aluno=self.aluno, turma=turma_outra_classe)

    def test_rejeita_director_de_turma_sem_turma(self):
        with self.assertRaises(ValidationError):
            AtribuicaoGestao.objects.create(
                professor=self.professor,
                escola=self.escola,
                ano_letivo=self.ano_letivo,
                cargo="director_turma",
            )

    def test_cria_coordenador_de_classe_com_escopo_valido(self):
        atribuicao = AtribuicaoGestao.objects.create(
            professor=self.professor,
            escola=self.escola,
            ano_letivo=self.ano_letivo,
            cargo="coordenador_classe",
            classe=self.classe,
        )

        self.assertEqual(atribuicao.classe, self.classe)

    def test_define_secundario_e_ciclo_1_para_classe_7(self):
        classe = Classe.objects.create(numero=7, ciclo=1)

        self.assertEqual(classe.nivel_ensino, "secundario")
        self.assertEqual(classe.ciclo, 1)
