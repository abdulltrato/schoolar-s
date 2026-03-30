from rest_framework import serializers
# Base de serializers do Django REST Framework.

from apps.school.models import Grade
# Modelo de classe escolar para relacionamentos.

from .models import (
    BaseCurriculum,
    Competency,
    CompetencyOutcome,
    CurriculumArea,
    LearningOutcome,
    LocalCurriculum,
    Subject,
    SubjectSpecialty,
    SubjectCurriculumPlan,
)
# Modelos de currículo utilizados nas APIs.


class CurriculumAreaSerializer(serializers.ModelSerializer):
    """Serializa áreas curriculares, garantindo default de deleção nula."""

    def to_internal_value(self, data):
        """Força presença de deleted_at para evitar validação de required."""
        # Copia request data para mutação segura.
        mutable = data.copy()
        # Define deleted_at nulo quando ausente.
        mutable.setdefault("deleted_at", None)
        # Delegar conversão padrão.
        return super().to_internal_value(mutable)

    def validate(self, attrs):
        """Garante que deleted_at sempre exista no objeto validado."""
        # Preenche deleted_at nulo se não vier no payload.
        attrs.setdefault("deleted_at", None)
        # Mantém validação padrão.
        return super().validate(attrs)

    class Meta:
        # Modelo base.
        model = CurriculumArea
        # Usa todos os campos do modelo.
        fields = "__all__"


class SubjectSerializer(serializers.ModelSerializer):
    """Serializa disciplina expondo área expandida e aceitando area_id."""

    # Representação detalhada de área em respostas.
    area = CurriculumAreaSerializer(read_only=True)
    # Campo de escrita para vincular área por ID.
    area_id = serializers.PrimaryKeyRelatedField(source="area", queryset=CurriculumArea.objects.all(), write_only=True)

    class Meta:
        # Modelo alvo.
        model = Subject
        # Todos os campos do modelo.
        fields = "__all__"


class SubjectSpecialtySerializer(serializers.ModelSerializer):
    """Serializa especialidades exibindo nome da disciplina."""

    # Campo calculado somente leitura para facilitar listagens.
    subject_name = serializers.CharField(source="subject.name", read_only=True)

    class Meta:
        # Modelo alvo.
        model = SubjectSpecialty
        # Todos os campos.
        fields = "__all__"


class CompetencySerializer(serializers.ModelSerializer):
    """Serializa competências com área e disciplina expandidas."""

    # Área detalhada em respostas.
    area = CurriculumAreaSerializer(read_only=True)
    # Campo de escrita para vincular área por ID.
    area_id = serializers.PrimaryKeyRelatedField(
        source="area",
        queryset=CurriculumArea.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    # Disciplina detalhada.
    subject = SubjectSerializer(read_only=True)
    # Campo de escrita para disciplina.
    subject_id = serializers.PrimaryKeyRelatedField(
        source="subject",
        queryset=Subject.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    # Classe vinculada (somente ID).
    grade = serializers.PrimaryKeyRelatedField(queryset=Grade.objects.all(), required=False, allow_null=True)

    class Meta:
        # Modelo alvo.
        model = Competency
        # Todos os campos.
        fields = "__all__"


class BaseCurriculumSerializer(serializers.ModelSerializer):
    """Serializa currículos base com competências expandidas e ids para escrita."""

    # Competências detalhadas na leitura.
    competencies = CompetencySerializer(many=True, read_only=True)
    # Lista de IDs aceita na escrita.
    competency_ids = serializers.PrimaryKeyRelatedField(
        source="competencies",
        queryset=Competency.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )

    class Meta:
        # Modelo alvo.
        model = BaseCurriculum
        # Todos os campos.
        fields = "__all__"

    def to_internal_value(self, data):
        """Normaliza payload aceitando campo legado competencia_ids."""
        # Copia dados para edição.
        normalized = data.copy()
        # Mapeia alias legado para o novo nome.
        if "competencia_ids" in normalized and "competency_ids" not in normalized:
            normalized["competency_ids"] = normalized["competencia_ids"]
        # Delega conversão padrão.
        return super().to_internal_value(normalized)


class LocalCurriculumSerializer(serializers.ModelSerializer):
    """Serializa currículos locais com competências adicionais."""

    # Competências extras detalhadas na resposta.
    additional_competencies = CompetencySerializer(many=True, read_only=True)
    # IDs aceitos no payload para escrever competências.
    competency_ids = serializers.PrimaryKeyRelatedField(
        source="additional_competencies",
        queryset=Competency.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )

    class Meta:
        # Modelo alvo.
        model = LocalCurriculum
        # Todos os campos.
        fields = "__all__"

    def to_internal_value(self, data):
        """Normaliza alias competencia_ids para competency_ids."""
        # Copia dados recebidos.
        normalized = data.copy()
        # Converte nome legado se necessário.
        if "competencia_ids" in normalized and "competency_ids" not in normalized:
            normalized["competency_ids"] = normalized["competencia_ids"]
        # Continua conversão padrão.
        return super().to_internal_value(normalized)


class SubjectCurriculumPlanSerializer(serializers.ModelSerializer):
    """Serializa planos curriculares por disciplina com metadados derivados."""

    # Nome da disciplina para leitura.
    subject_name = serializers.CharField(source="grade_subject.subject.name", read_only=True)
    # Número da classe para leitura.
    grade_number = serializers.IntegerField(source="grade_subject.grade.number", read_only=True)
    # Código do ano letivo.
    academic_year_code = serializers.CharField(source="grade_subject.academic_year.code", read_only=True)
    # Competências planejadas detalhadas.
    planned_competencies = CompetencySerializer(many=True, read_only=True)
    # IDs aceitos na escrita.
    competency_ids = serializers.PrimaryKeyRelatedField(
        source="planned_competencies",
        queryset=Competency.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )

    class Meta:
        # Modelo alvo.
        model = SubjectCurriculumPlan
        # Todos os campos.
        fields = "__all__"

    def to_internal_value(self, data):
        """Aceita campo legado competencia_ids no payload."""
        # Copia para mutação segura.
        normalized = data.copy()
        # Mapeia nome legado se presente.
        if "competencia_ids" in normalized and "competency_ids" not in normalized:
            normalized["competency_ids"] = normalized["competencia_ids"]
        # Delega conversão padrão.
        return super().to_internal_value(normalized)


class LearningOutcomeSerializer(serializers.ModelSerializer):
    """Serializa resultados de aprendizagem com campos derivados."""

    # Nome da disciplina na leitura.
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    # Número da classe na leitura.
    grade_number = serializers.IntegerField(source="grade.number", read_only=True)

    class Meta:
        # Modelo alvo.
        model = LearningOutcome
        # Todos os campos.
        fields = "__all__"
        # Código é gerado automaticamente e não pode ser escrito.
        read_only_fields = ("code",)


class CompetencyOutcomeSerializer(serializers.ModelSerializer):
    """Serializa alinhamentos entre competência e resultado com nomes auxiliares."""

    # Nome da competência para leitura.
    competency_name = serializers.CharField(source="competency.name", read_only=True)
    # Código do resultado.
    outcome_code = serializers.CharField(source="outcome.code", read_only=True)
    # Descrição do resultado.
    outcome_description = serializers.CharField(source="outcome.description", read_only=True)

    class Meta:
        # Modelo alvo.
        model = CompetencyOutcome
        # Todos os campos.
        fields = "__all__"
