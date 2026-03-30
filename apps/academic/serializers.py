from rest_framework import serializers

# Importa todos os modelos usados pelos serializers.
from .models import (
    Guardian,
    Student,
    StudentCompetency,
    StudentGuardian,
    StudentOutcome,
)


# Serializer para a relação de competência do aluno.
class StudentCompetencySerializer(serializers.ModelSerializer):
    # Exibe o nome da competência relacionada (somente leitura).
    competency_name = serializers.CharField(source="competency.name", read_only=True)
    # Campo calculado que replica o nível armazenado em `nivel`.
    level = serializers.DecimalField(
        source="nivel", max_digits=3, decimal_places=1, read_only=True
    )

    class Meta:
        # Modelo de origem do serializer.
        model = StudentCompetency
        # Campos expostos na API.
        fields = ["id", "code", "competency", "competency_name", "level", "updated_at"]


# Serializer para os resultados de aprendizagem do aluno.
class StudentOutcomeSerializer(serializers.ModelSerializer):
    # Código do resultado relacionado (somente leitura).
    outcome_code = serializers.CharField(source="outcome.code", read_only=True)
    # Descrição textual do resultado (somente leitura).
    outcome_description = serializers.CharField(
        source="outcome.description", read_only=True
    )
    # Nível de taxonomia do resultado (somente leitura).
    taxonomy_level = serializers.CharField(
        source="outcome.taxonomy_level", read_only=True
    )
    # Dimensão do conhecimento associada (somente leitura).
    knowledge_dimension = serializers.CharField(
        source="outcome.knowledge_dimension", read_only=True
    )

    class Meta:
        # Modelo representado.
        model = StudentOutcome
        # Exibe todos os campos do modelo e dos adicionais mapeados.
        fields = "__all__"


# Serializer principal de alunos.
class StudentSerializer(serializers.ModelSerializer):
    # Serializa competências vinculadas usando o serializer acima.
    competencies = StudentCompetencySerializer(
        source="studentcompetency_set", many=True, read_only=True
    )
    # Serializa resultados vinculados.
    outcomes = StudentOutcomeSerializer(
        source="studentoutcome_set", many=True, read_only=True
    )
    # Exibe ciclo calculado como campo somente leitura.
    cycle = serializers.IntegerField(read_only=True)
    # Exibe nível de ensino calculado como somente leitura.
    education_level = serializers.CharField(read_only=True)
    # Exibe código do ciclo escolar relacionado.
    cycle_model_code = serializers.CharField(source="cycle_model.code", read_only=True)
    # Exibe nome do ciclo escolar relacionado.
    cycle_model_name = serializers.CharField(source="cycle_model.name", read_only=True)
    # Exibe nível técnico preenchido no modelo.
    technical_level = serializers.CharField(read_only=True)
    # Exibe ramo de ensino (general/technical).
    education_path = serializers.CharField(read_only=True)
    # Renomeia o campo estado para status na API.
    status = serializers.CharField(source="estado")

    class Meta:
        # Modelo representado.
        model = Student
        # Lista explícita dos campos retornados pela API.
        fields = [
            "id",
            "code",
            "user",
            "name",
            "tenant_id",
            "birth_date",
            "grade",
            "cycle",
            "cycle_model",
            "cycle_model_code",
            "cycle_model_name",
            "education_level",
            "education_path",
            "technical_level",
            "status",
            "identification_document",
            "previous_certificate",
            "competencies",
            "outcomes",
            "created_at",
            "updated_at",
            "deleted_at",
        ]


# Serializer direto para o modelo de encarregado.
class GuardianSerializer(serializers.ModelSerializer):
    class Meta:
        # Modelo representado.
        model = Guardian
        # Exibe todos os campos do modelo.
        fields = "__all__"


# Serializer para o vínculo aluno-encarregado.
class StudentGuardianSerializer(serializers.ModelSerializer):
    # Nome do aluno relacionado (somente leitura).
    student_name = serializers.CharField(source="student.name", read_only=True)
    # Nome do encarregado relacionado (somente leitura).
    guardian_name = serializers.CharField(source="guardian.name", read_only=True)

    class Meta:
        # Modelo representado.
        model = StudentGuardian
        # Exibe todos os campos do modelo mais os calculados.
        fields = "__all__"
