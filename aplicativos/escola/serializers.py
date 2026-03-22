from rest_framework import serializers

from .models import (
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


class AnoLetivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnoLetivo
        fields = "__all__"


class ClasseSerializer(serializers.ModelSerializer):
    nivel_ensino = serializers.CharField(read_only=True)

    class Meta:
        model = Classe
        fields = ["id", "numero", "ciclo", "nivel_ensino", "nome"]


class EscolaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Escola
        fields = "__all__"


class ProfessorSerializer(serializers.ModelSerializer):
    escola_nome = serializers.CharField(source="escola.nome", read_only=True)

    class Meta:
        model = Professor
        fields = "__all__"


class TurmaSerializer(serializers.ModelSerializer):
    classe = serializers.SlugRelatedField(slug_field="numero", queryset=Classe.objects.all())
    ano_letivo = serializers.SlugRelatedField(slug_field="codigo", queryset=AnoLetivo.objects.all())
    classe_nome = serializers.CharField(source="classe.nome", read_only=True)
    escola_nome = serializers.CharField(source="escola.nome", read_only=True)
    professor_responsavel_nome = serializers.CharField(source="professor_responsavel.nome", read_only=True)

    class Meta:
        model = Turma
        fields = "__all__"


class DisciplinaClasseSerializer(serializers.ModelSerializer):
    ano_letivo = serializers.SlugRelatedField(slug_field="codigo", queryset=AnoLetivo.objects.all())
    classe = serializers.SlugRelatedField(slug_field="numero", queryset=Classe.objects.all())
    disciplina_nome = serializers.CharField(source="disciplina.nome", read_only=True)

    class Meta:
        model = DisciplinaClasse
        fields = "__all__"


class AlocacaoDocenteSerializer(serializers.ModelSerializer):
    professor_nome = serializers.CharField(source="professor.nome", read_only=True)
    turma_nome = serializers.CharField(source="turma.nome", read_only=True)
    escola_nome = serializers.CharField(source="turma.escola.nome", read_only=True)
    disciplina_nome = serializers.CharField(source="disciplina_classe.disciplina.nome", read_only=True)
    ano_letivo = serializers.CharField(source="disciplina_classe.ano_letivo.codigo", read_only=True)
    classe = serializers.IntegerField(source="disciplina_classe.classe.numero", read_only=True)

    class Meta:
        model = AlocacaoDocente
        fields = "__all__"


class MatriculaSerializer(serializers.ModelSerializer):
    aluno_nome = serializers.CharField(source="aluno.nome", read_only=True)
    turma_nome = serializers.CharField(source="turma.nome", read_only=True)
    escola_nome = serializers.CharField(source="turma.escola.nome", read_only=True)
    ano_letivo = serializers.CharField(source="turma.ano_letivo.codigo", read_only=True)
    classe = serializers.IntegerField(source="turma.classe.numero", read_only=True)

    class Meta:
        model = Matricula
        fields = "__all__"


class AtribuicaoGestaoSerializer(serializers.ModelSerializer):
    professor_nome = serializers.CharField(source="professor.nome", read_only=True)
    escola_nome = serializers.CharField(source="escola.nome", read_only=True)
    ano_letivo_codigo = serializers.CharField(source="ano_letivo.codigo", read_only=True)
    classe_numero = serializers.IntegerField(source="classe.numero", read_only=True)
    turma_nome = serializers.CharField(source="turma.nome", read_only=True)

    class Meta:
        model = AtribuicaoGestao
        fields = "__all__"
