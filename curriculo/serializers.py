from rest_framework import serializers
from .models import AreaCurricular, Disciplina, Competencia, CurriculoBase, CurriculoLocal


class AreaCurricularSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaCurricular
        fields = '__all__'


class DisciplinaSerializer(serializers.ModelSerializer):
    area = AreaCurricularSerializer(read_only=True)
    area_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Disciplina
        fields = '__all__'


class CompetenciaSerializer(serializers.ModelSerializer):
    disciplina = DisciplinaSerializer(read_only=True)
    disciplina_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Competencia
        fields = '__all__'


class CurriculoBaseSerializer(serializers.ModelSerializer):
    competencias = CompetenciaSerializer(many=True, read_only=True)

    class Meta:
        model = CurriculoBase
        fields = '__all__'


class CurriculoLocalSerializer(serializers.ModelSerializer):
    competencias_adicionais = CompetenciaSerializer(many=True, read_only=True)

    class Meta:
        model = CurriculoLocal
        fields = '__all__'
