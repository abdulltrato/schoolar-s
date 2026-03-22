from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from aplicativos.academico.models import Aluno
from aplicativos.avaliacao.models import (
    Avaliacao,
    ComponenteAvaliativa,
    PeriodoAvaliativo,
    ResultadoPeriodoDisciplina,
)
from aplicativos.curriculo.models import (
    AreaCurricular,
    Competencia,
    Disciplina,
    PlanoCurricularDisciplina,
)
from aplicativos.escola.models import (
    AlocacaoDocente,
    AnoLetivo,
    AtribuicaoGestao,
    Classe,
    DisciplinaClasse,
    Escola,
    Matricula,
    Professor,
    Turma,
)


class Command(BaseCommand):
    help = "Cria dados mínimos de demonstração para integrar backend e frontend localmente."

    def handle(self, *args, **options):
        user_model = get_user_model()

        admin, _ = user_model.objects.get_or_create(
            username="admin",
            defaults={"is_staff": True, "is_superuser": True},
        )
        admin.set_password("secret")
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()

        professor_user, _ = user_model.objects.get_or_create(username="prof1")
        professor_user.set_password("secret")
        professor_user.save()

        escola, _ = Escola.objects.get_or_create(
            codigo="ESC-CENTRAL",
            defaults={
                "nome": "Escola Primaria Central",
                "distrito": "KaMpfumo",
                "provincia": "Maputo Cidade",
                "ativa": True,
            },
        )

        ano_letivo, _ = AnoLetivo.objects.get_or_create(
            codigo="2026-2027",
            defaults={
                "data_inicio": date(2026, 2, 1),
                "data_fim": date(2026, 12, 15),
                "ativo": True,
            },
        )

        classe_2, _ = Classe.objects.get_or_create(numero=2, defaults={"ciclo": 1, "nome": "2a Classe"})
        classe_5, _ = Classe.objects.get_or_create(numero=5, defaults={"ciclo": 2, "nome": "5a Classe"})

        professor, _ = Professor.objects.get_or_create(
            user=professor_user,
            defaults={
                "nome": "Prof. Ana Lemos",
                "especialidade": "Matematica",
                "escola": escola,
            },
        )
        if professor.escola_id != escola.id:
            professor.escola = escola
            professor.save()

        turma_a, _ = Turma.objects.get_or_create(
            nome="Turma A",
            classe=classe_2,
            ano_letivo=ano_letivo,
            defaults={
                "escola": escola,
                "ciclo": classe_2.ciclo,
                "professor_responsavel": professor,
            },
        )
        turma_b, _ = Turma.objects.get_or_create(
            nome="Turma B",
            classe=classe_5,
            ano_letivo=ano_letivo,
            defaults={
                "escola": escola,
                "ciclo": classe_5.ciclo,
                "professor_responsavel": professor,
            },
        )
        for turma in (turma_a, turma_b):
            changed = False
            if turma.escola_id != escola.id:
                turma.escola = escola
                changed = True
            if turma.professor_responsavel_id != professor.id:
                turma.professor_responsavel = professor
                changed = True
            if changed:
                turma.save()

        area, _ = AreaCurricular.objects.get_or_create(nome="Ciencias Naturais e Matematica")
        matematica_1, _ = Disciplina.objects.get_or_create(nome="Matematica", area=area, ciclo=1)
        matematica_2, _ = Disciplina.objects.get_or_create(nome="Matematica Avancada", area=area, ciclo=2)

        competencia_1, _ = Competencia.objects.get_or_create(
            nome="Resolver operacoes basicas",
            defaults={
                "area": "saber_cientifico_tecnologico",
                "ciclo": 1,
                "disciplina": matematica_1,
            },
        )
        competencia_2, _ = Competencia.objects.get_or_create(
            nome="Resolver problemas fraccionarios",
            defaults={
                "area": "saber_cientifico_tecnologico",
                "ciclo": 2,
                "disciplina": matematica_2,
            },
        )

        dc_2, _ = DisciplinaClasse.objects.get_or_create(
            ano_letivo=ano_letivo,
            classe=classe_2,
            disciplina=matematica_1,
            defaults={"carga_horaria_semanal": 5},
        )
        dc_5, _ = DisciplinaClasse.objects.get_or_create(
            ano_letivo=ano_letivo,
            classe=classe_5,
            disciplina=matematica_2,
            defaults={"carga_horaria_semanal": 5},
        )

        alocacao_2, _ = AlocacaoDocente.objects.get_or_create(
            professor=professor,
            turma=turma_a,
            disciplina_classe=dc_2,
        )
        alocacao_5, _ = AlocacaoDocente.objects.get_or_create(
            professor=professor,
            turma=turma_b,
            disciplina_classe=dc_5,
        )

        aluno_1, _ = Aluno.objects.get_or_create(
            nome="Ana Silva",
            defaults={
                "data_nascimento": date(2016, 3, 10),
                "classe": 2,
                "ciclo": 1,
                "estado": "ativo",
            },
        )
        aluno_2, _ = Aluno.objects.get_or_create(
            nome="Beto Mussa",
            defaults={
                "data_nascimento": date(2013, 5, 4),
                "classe": 5,
                "ciclo": 2,
                "estado": "ativo",
            },
        )

        Matricula.objects.get_or_create(aluno=aluno_1, turma=turma_a)
        Matricula.objects.get_or_create(aluno=aluno_2, turma=turma_b)

        for cargo, extra in (
            ("director_escola", {}),
            ("director_adjunto_pedagogico", {}),
            ("director_ciclo", {"ciclo": 1}),
            ("coordenador_classe", {"classe": classe_2}),
            ("director_turma", {"turma": turma_a}),
        ):
            AtribuicaoGestao.objects.get_or_create(
                professor=professor,
                escola=escola,
                ano_letivo=ano_letivo,
                cargo=cargo,
                defaults=extra,
            )

        plano_2, _ = PlanoCurricularDisciplina.objects.get_or_create(
            disciplina_classe=dc_2,
            defaults={
                "objetivos": "Consolidar operacoes basicas e numeracao.",
                "metodologia": "Aulas praticas com resolucao guiada.",
                "criterios_avaliacao": "Participacao, testes e trabalhos individuais.",
                "ativo": True,
            },
        )
        plano_2.competencias_previstas.set([competencia_1])

        plano_5, _ = PlanoCurricularDisciplina.objects.get_or_create(
            disciplina_classe=dc_5,
            defaults={
                "objetivos": "Desenvolver fraccoes e problemas compostos.",
                "metodologia": "Aprendizagem orientada por problemas.",
                "criterios_avaliacao": "ACS, ACP, teste e exame.",
                "ativo": True,
            },
        )
        plano_5.competencias_previstas.set([competencia_2])

        periodo_1, _ = PeriodoAvaliativo.objects.get_or_create(
            ano_letivo=ano_letivo,
            ordem=1,
            defaults={
                "nome": "1o Trimestre",
                "data_inicio": date(2026, 2, 1),
                "data_fim": date(2026, 4, 30),
                "ativo": True,
            },
        )

        componente_acs, _ = ComponenteAvaliativa.objects.get_or_create(
            periodo=periodo_1,
            disciplina_classe=dc_2,
            nome="ACS 1",
            defaults={
                "tipo": "acs",
                "peso": Decimal("40.00"),
                "nota_maxima": Decimal("20.00"),
                "obrigatoria": True,
            },
        )
        componente_exame, _ = ComponenteAvaliativa.objects.get_or_create(
            periodo=periodo_1,
            disciplina_classe=dc_2,
            nome="Exame 1",
            defaults={
                "tipo": "exame",
                "peso": Decimal("60.00"),
                "nota_maxima": Decimal("20.00"),
                "obrigatoria": True,
            },
        )

        Avaliacao.objects.get_or_create(
            aluno=aluno_1,
            alocacao_docente=alocacao_2,
            periodo=periodo_1,
            componente=componente_acs,
            defaults={
                "competencia": competencia_1,
                "tipo": "acs",
                "data": date(2026, 3, 15),
                "nota": Decimal("14.0"),
                "comentario": "Bom desempenho nas operacoes basicas.",
                "conhecimentos": True,
            },
        )
        Avaliacao.objects.get_or_create(
            aluno=aluno_1,
            alocacao_docente=alocacao_2,
            periodo=periodo_1,
            componente=componente_exame,
            defaults={
                "competencia": competencia_1,
                "tipo": "exame",
                "data": date(2026, 4, 20),
                "nota": Decimal("16.0"),
                "comentario": "Evolucao consistente no trimestre.",
                "habilidades": True,
            },
        )

        ResultadoPeriodoDisciplina.recalcular(
            aluno=aluno_1,
            alocacao_docente=alocacao_2,
            periodo=periodo_1,
        )

        self.stdout.write(self.style.SUCCESS("Dados de demonstração carregados com sucesso."))
