#!/usr/bin/env python
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'schoolar_s.settings')
django.setup()

from aplicativos.academico.models import Aluno
from aplicativos.curriculo.models import AreaCurricular, Disciplina, Competencia, CurriculoBase, CurriculoLocal
from aplicativos.avaliacao.models import Avaliacao
from aplicativos.progresso.models import Progressao
from aplicativos.escola.models import Professor, Turma, Matricula
from aplicativos.relatorios.models import Relatorio
from aplicativos.eventos.models import Evento
from django.contrib.auth.models import User

def test_models():
    print("Iniciando testes dos modelos...")

    # Teste Academico
    try:
        aluno = Aluno.objects.create(
            nome="Joao Silva",
            data_nascimento="2010-05-15",
            classe=1,
            ciclo=1,
            estado="ativo"
        )
        print(f"✓ Aluno criado: {aluno}")
    except Exception as e:
        print(f"✗ Erro em Aluno: {e}")

    # Teste Curriculo
    try:
        area = AreaCurricular.objects.create(nome="Ciencias Naturais")
        print(f"✓ Area Curricular criada: {area}")

        disciplina = Disciplina.objects.create(
            nome="Matematica",
            area=area,
            ciclo=1
        )
        print(f"✓ Disciplina criada: {disciplina}")

        competencia = Competencia.objects.create(
            nome="Resolver problemas matematicos",
            descricao="Competencia em matematica basica",
            area="saber_cientifico_tecnologico",
            ciclo=1,
            disciplina=disciplina
        )
        print(f"✓ Competencia criada: {competencia}")

        curriculo_base = CurriculoBase.objects.create(ciclo=1)
        curriculo_base.competencias.add(competencia)
        print(f"✓ Curriculo Base criado: {curriculo_base}")

        curriculo_local = CurriculoLocal.objects.create(
            tenant_id="escola1",
            ciclo=1
        )
        print(f"✓ Curriculo Local criado: {curriculo_local}")

    except Exception as e:
        print(f"✗ Erro em Curriculo: {e}")

    # Teste Avaliacao
    try:
        avaliacao = Avaliacao.objects.create(
            aluno=aluno,
            competencia=competencia,
            tipo="formativa",
            data="2023-10-01",
            comentario="Bom desempenho",
            conhecimentos=True,
            habilidades=True,
            atitudes=False
        )
        print(f"✓ Avaliacao criada: {avaliacao}")
    except Exception as e:
        print(f"✗ Erro em Avaliacao: {e}")

    # Teste Progresso
    try:
        progresso = Progressao.objects.create(
            aluno=aluno,
            ciclo=1,
            ano_letivo="2023-2024",
            data_decisao="2024-06-15",
            decisao="aprovado",
            comentario="Aprovado com sucesso"
        )
        print(f"✓ Progressao criada: {progresso}")
    except Exception as e:
        print(f"✗ Erro em Progresso: {e}")

    # Teste Escola
    try:
        user = User.objects.create_user(username="prof1", password="pass123")
        professor = Professor.objects.create(
            user=user,
            nome="Prof. Maria",
            especialidade="Matematica"
        )
        print(f"✓ Professor criado: {professor}")

        turma = Turma.objects.create(
            nome="Turma A",
            ciclo=1,
            ano_letivo="2023-2024",
            professor_responsavel=professor
        )
        print(f"✓ Turma criada: {turma}")

        matricula = Matricula.objects.create(
            aluno=aluno,
            turma=turma
        )
        print(f"✓ Matricula criada: {matricula}")
    except Exception as e:
        print(f"✗ Erro em Escola: {e}")

    # Teste Relatorios
    try:
        relatorio = Relatorio.objects.create(
            titulo="Relatorio de Aluno Joao",
            tipo="aluno",
            periodo="2023-2024",
            conteudo={"notas": [8, 9, 7]},
            aluno=aluno
        )
        print(f"✓ Relatorio criado: {relatorio}")
    except Exception as e:
        print(f"✗ Erro em Relatorios: {e}")

    # Teste Eventos
    try:
        evento = Evento.objects.create(
            tipo="aluno_registrado",
            dados={"aluno_id": aluno.id},
            tenant_id="escola1"
        )
        print(f"✓ Evento criado: {evento}")
    except Exception as e:
        print(f"✗ Erro em Eventos: {e}")

    print("Testes concluidos!")

if __name__ == "__main__":
    test_models()
