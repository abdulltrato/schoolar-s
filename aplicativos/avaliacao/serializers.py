from rest_framework import serializers

from .models import Avaliacao, ComponenteAvaliativa, PeriodoAvaliativo, ResultadoPeriodoDisciplina


class PeriodoAvaliativoSerializer(serializers.ModelSerializer):
    ano_letivo_codigo = serializers.CharField(source="ano_letivo.codigo", read_only=True)

    class Meta:
        model = PeriodoAvaliativo
        fields = "__all__"


class ComponenteAvaliativaSerializer(serializers.ModelSerializer):
    periodo_nome = serializers.CharField(source="periodo.nome", read_only=True)
    disciplina_nome = serializers.CharField(source="disciplina_classe.disciplina.nome", read_only=True)
    classe = serializers.IntegerField(source="disciplina_classe.classe.numero", read_only=True)
    ano_letivo = serializers.CharField(source="disciplina_classe.ano_letivo.codigo", read_only=True)

    class Meta:
        model = ComponenteAvaliativa
        fields = "__all__"


class AvaliacaoSerializer(serializers.ModelSerializer):
    aluno_nome = serializers.CharField(source="aluno.nome", read_only=True)
    competencia_nome = serializers.CharField(source="competencia.nome", read_only=True)
    professor_nome = serializers.CharField(source="alocacao_docente.professor.nome", read_only=True)
    turma_nome = serializers.CharField(source="alocacao_docente.turma.nome", read_only=True)
    disciplina_nome = serializers.CharField(
        source="alocacao_docente.disciplina_classe.disciplina.nome",
        read_only=True,
    )
    ano_letivo = serializers.CharField(source="alocacao_docente.turma.ano_letivo.codigo", read_only=True)
    classe = serializers.IntegerField(source="alocacao_docente.turma.classe.numero", read_only=True)
    periodo_nome = serializers.CharField(source="periodo.nome", read_only=True)
    componente_nome = serializers.CharField(source="componente.nome", read_only=True)

    class Meta:
        model = Avaliacao
        fields = "__all__"


class ResultadoPeriodoDisciplinaSerializer(serializers.ModelSerializer):
    aluno_nome = serializers.CharField(source="aluno.nome", read_only=True)
    professor_nome = serializers.CharField(source="alocacao_docente.professor.nome", read_only=True)
    turma_nome = serializers.CharField(source="alocacao_docente.turma.nome", read_only=True)
    disciplina_nome = serializers.CharField(source="alocacao_docente.disciplina_classe.disciplina.nome", read_only=True)
    periodo_nome = serializers.CharField(source="periodo.nome", read_only=True)

    class Meta:
        model = ResultadoPeriodoDisciplina
        fields = "__all__"
