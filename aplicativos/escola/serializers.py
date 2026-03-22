from rest_framework import serializers
from .models import Professor, Turma, Matricula


class ProfessorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professor
        fields = '__all__'


class TurmaSerializer(serializers.ModelSerializer):
    professor_responsavel_nome = serializers.CharField(source='professor_responsavel.nome', read_only=True)

    class Meta:
        model = Turma
        fields = '__all__'


class MatriculaSerializer(serializers.ModelSerializer):
    aluno_nome = serializers.CharField(source='aluno.nome', read_only=True)
    turma_nome = serializers.CharField(source='turma.nome', read_only=True)

    class Meta:
        model = Matricula
        fields = '__all__'
