from rest_framework import serializers
from .models import Avaliacao


class AvaliacaoSerializer(serializers.ModelSerializer):
    aluno_nome = serializers.CharField(source='aluno.nome', read_only=True)
    competencia_nome = serializers.CharField(source='competencia.nome', read_only=True)

    class Meta:
        model = Avaliacao
        fields = '__all__'
