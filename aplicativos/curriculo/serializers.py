from rest_framework import serializers

from .models import AreaCurricular, Competencia, CurriculoBase, CurriculoLocal, Disciplina, PlanoCurricularDisciplina


class AreaCurricularSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaCurricular
        fields = "__all__"


class DisciplinaSerializer(serializers.ModelSerializer):
    area = AreaCurricularSerializer(read_only=True)
    area_id = serializers.PrimaryKeyRelatedField(source="area", queryset=AreaCurricular.objects.all(), write_only=True)

    class Meta:
        model = Disciplina
        fields = "__all__"


class CompetenciaSerializer(serializers.ModelSerializer):
    disciplina = DisciplinaSerializer(read_only=True)
    disciplina_id = serializers.PrimaryKeyRelatedField(
        source="disciplina",
        queryset=Disciplina.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Competencia
        fields = "__all__"


class CurriculoBaseSerializer(serializers.ModelSerializer):
    competencias = CompetenciaSerializer(many=True, read_only=True)
    competencia_ids = serializers.PrimaryKeyRelatedField(
        source="competencias",
        queryset=Competencia.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )

    class Meta:
        model = CurriculoBase
        fields = "__all__"


class CurriculoLocalSerializer(serializers.ModelSerializer):
    competencias_adicionais = CompetenciaSerializer(many=True, read_only=True)
    competencia_ids = serializers.PrimaryKeyRelatedField(
        source="competencias_adicionais",
        queryset=Competencia.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )

    class Meta:
        model = CurriculoLocal
        fields = "__all__"


class PlanoCurricularDisciplinaSerializer(serializers.ModelSerializer):
    disciplina_nome = serializers.CharField(source="disciplina_classe.disciplina.nome", read_only=True)
    classe = serializers.IntegerField(source="disciplina_classe.classe.numero", read_only=True)
    ano_letivo = serializers.CharField(source="disciplina_classe.ano_letivo.codigo", read_only=True)
    competencias_previstas = CompetenciaSerializer(many=True, read_only=True)
    competencia_ids = serializers.PrimaryKeyRelatedField(
        source="competencias_previstas",
        queryset=Competencia.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )

    class Meta:
        model = PlanoCurricularDisciplina
        fields = "__all__"
