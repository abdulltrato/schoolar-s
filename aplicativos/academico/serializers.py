from rest_framework import serializers
from .models import Aluno, AlunoCompetencia


class AlunoCompetenciaSerializer(serializers.ModelSerializer):
    competencia_nome = serializers.CharField(source='competencia.nome', read_only=True)

    class Meta:
        model = AlunoCompetencia
        fields = ['id', 'competencia', 'competencia_nome', 'nivel', 'data_atualizacao']


class AlunoSerializer(serializers.ModelSerializer):
    competencias = AlunoCompetenciaSerializer(source='alunocompetencia_set', many=True, read_only=True)

    class Meta:
        model = Aluno
        fields = ['id', 'nome', 'data_nascimento', 'classe', 'ciclo', 'estado', 'competencias']
