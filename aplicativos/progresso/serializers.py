from rest_framework import serializers
from .models import Progressao


class ProgressaoSerializer(serializers.ModelSerializer):
    aluno_nome = serializers.CharField(source='aluno.nome', read_only=True)

    class Meta:
        model = Progressao
        fields = '__all__'
