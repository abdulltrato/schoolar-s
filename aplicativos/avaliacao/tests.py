from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from aplicativos.academico.models import Aluno
from aplicativos.curriculo.models import AreaCurricular, Competencia, Disciplina
from aplicativos.escola.models import AlocacaoDocente, AnoLetivo, Classe, DisciplinaClasse, Escola, Matricula, Professor, Turma
from .models import Avaliacao, ComponenteAvaliativa, PeriodoAvaliativo, ResultadoPeriodoDisciplina


class AvaliacaoModelTests(TestCase):
    def setUp(self):
        self.escola = Escola.objects.create(codigo="ESC-01", nome="Escola Primaria Central")
        user = get_user_model().objects.create_user(username="prof", password="secret")
        self.professor = Professor.objects.create(user=user, nome="Prof. Ana", escola=self.escola)
        self.ano_letivo = AnoLetivo.objects.create(
            codigo="2026-2027",
            data_inicio=date(2026, 2, 1),
            data_fim=date(2026, 12, 15),
            ativo=True,
        )
        self.periodo = PeriodoAvaliativo.objects.create(
            ano_letivo=self.ano_letivo,
            nome="1o Trimestre",
            ordem=1,
            data_inicio=date(2026, 2, 1),
            data_fim=date(2026, 4, 30),
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
        self.aluno = Aluno.objects.create(
            nome="Ana",
            data_nascimento=date(2016, 2, 1),
            classe=2,
            ciclo=1,
        )
        Matricula.objects.create(aluno=self.aluno, turma=self.turma)

        area = AreaCurricular.objects.create(nome="Ciencias Naturais")
        self.disciplina = Disciplina.objects.create(nome="Matematica", area=area, ciclo=1)
        self.outra_disciplina = Disciplina.objects.create(nome="Historia", area=area, ciclo=1)
        self.disciplina_classe = DisciplinaClasse.objects.create(
            ano_letivo=self.ano_letivo,
            classe=self.classe,
            disciplina=self.disciplina,
        )
        self.alocacao = AlocacaoDocente.objects.create(
            professor=self.professor,
            turma=self.turma,
            disciplina_classe=self.disciplina_classe,
        )
        self.componente_teste = ComponenteAvaliativa.objects.create(
            periodo=self.periodo,
            disciplina_classe=self.disciplina_classe,
            tipo="teste",
            nome="Teste 1",
            peso=Decimal("40.00"),
            nota_maxima=Decimal("20.00"),
        )
        self.componente_exame = ComponenteAvaliativa.objects.create(
            periodo=self.periodo,
            disciplina_classe=self.disciplina_classe,
            tipo="exame",
            nome="Exame Final",
            peso=Decimal("60.00"),
            nota_maxima=Decimal("20.00"),
        )
        self.competencia = Competencia.objects.create(
            nome="Resolver operacoes basicas",
            area="saber_cientifico_tecnologico",
            ciclo=1,
            disciplina=self.disciplina,
        )
        self.competencia_outra_disciplina = Competencia.objects.create(
            nome="Interpretar factos historicos",
            area="linguagem_comunicacao",
            ciclo=1,
            disciplina=self.outra_disciplina,
        )

    def test_rejeita_avaliacao_de_aluno_nao_matriculado_na_turma(self):
        outro_aluno = Aluno.objects.create(
            nome="Beto",
            data_nascimento=date(2016, 5, 1),
            classe=2,
            ciclo=1,
        )

        with self.assertRaises(ValidationError):
            Avaliacao.objects.create(
                aluno=outro_aluno,
                alocacao_docente=self.alocacao,
                periodo=self.periodo,
                componente=self.componente_teste,
                tipo="teste",
                data=date(2026, 3, 1),
                nota=14,
            )

    def test_rejeita_avaliacao_com_competencia_de_outra_disciplina(self):
        with self.assertRaises(ValidationError):
            Avaliacao.objects.create(
                aluno=self.aluno,
                alocacao_docente=self.alocacao,
                periodo=self.periodo,
                componente=self.componente_teste,
                competencia=self.competencia_outra_disciplina,
                tipo="teste",
                data=date(2026, 3, 1),
                nota=15,
            )

    def test_rejeita_avaliacao_com_nota_acima_da_componente(self):
        with self.assertRaises(ValidationError):
            Avaliacao.objects.create(
                aluno=self.aluno,
                alocacao_docente=self.alocacao,
                periodo=self.periodo,
                componente=self.componente_teste,
                competencia=self.competencia,
                tipo="teste",
                data=date(2026, 3, 1),
                nota=21,
            )

    def test_calcula_media_ponderada_por_periodo(self):
        Avaliacao.objects.create(
            aluno=self.aluno,
            alocacao_docente=self.alocacao,
            periodo=self.periodo,
            componente=self.componente_teste,
            competencia=self.competencia,
            tipo="teste",
            data=date(2026, 3, 1),
            nota=Decimal("10.0"),
        )
        Avaliacao.objects.create(
            aluno=self.aluno,
            alocacao_docente=self.alocacao,
            periodo=self.periodo,
            componente=self.componente_exame,
            competencia=self.competencia,
            tipo="exame",
            data=date(2026, 4, 20),
            nota=Decimal("20.0"),
        )

        resultado = ResultadoPeriodoDisciplina.recalcular(
            aluno=self.aluno,
            alocacao_docente=self.alocacao,
            periodo=self.periodo,
        )

        self.assertEqual(resultado.avaliacoes_consideradas, 2)
        self.assertEqual(resultado.media_final, Decimal("16.00"))

    def test_atualiza_resultado_automaticamente_ao_salvar_avaliacoes(self):
        Avaliacao.objects.create(
            aluno=self.aluno,
            alocacao_docente=self.alocacao,
            periodo=self.periodo,
            componente=self.componente_teste,
            competencia=self.competencia,
            tipo="teste",
            data=date(2026, 3, 1),
            nota=Decimal("10.0"),
        )
        Avaliacao.objects.create(
            aluno=self.aluno,
            alocacao_docente=self.alocacao,
            periodo=self.periodo,
            componente=self.componente_exame,
            competencia=self.competencia,
            tipo="exame",
            data=date(2026, 4, 20),
            nota=Decimal("20.0"),
        )

        resultado = ResultadoPeriodoDisciplina.objects.get(
            aluno=self.aluno,
            alocacao_docente=self.alocacao,
            periodo=self.periodo,
        )

        self.assertEqual(resultado.avaliacoes_consideradas, 2)
        self.assertEqual(resultado.media_final, Decimal("16.00"))

    def test_remove_resultado_quando_ultima_avaliacao_e_apagada(self):
        avaliacao = Avaliacao.objects.create(
            aluno=self.aluno,
            alocacao_docente=self.alocacao,
            periodo=self.periodo,
            componente=self.componente_teste,
            competencia=self.competencia,
            tipo="teste",
            data=date(2026, 3, 1),
            nota=Decimal("10.0"),
        )

        self.assertTrue(
            ResultadoPeriodoDisciplina.objects.filter(
                aluno=self.aluno,
                alocacao_docente=self.alocacao,
                periodo=self.periodo,
            ).exists()
        )

        avaliacao.delete()

        self.assertFalse(
            ResultadoPeriodoDisciplina.objects.filter(
                aluno=self.aluno,
                alocacao_docente=self.alocacao,
                periodo=self.periodo,
            ).exists()
        )
