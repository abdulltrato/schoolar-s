from rest_framework import serializers
# Importa base de serializers do DRF.

from core.serializers import TenantAcademicYearField
# Campo customizado que resolve ano letivo a partir do tenant.

from .models import Assessment, AssessmentComponent, AssessmentOutcomeMap, AssessmentPeriod, SubjectPeriodResult
# Importa modelos usados nos serializers.


class AssessmentPeriodSerializer(serializers.ModelSerializer):
    """Serializer para períodos avaliativos, garantindo preenchimento de deleted_at."""

    # Campo customizado que entende o tenant do ano letivo.
    academic_year = TenantAcademicYearField()
    # Exposição do código do ano letivo em modo somente leitura.
    academic_year_code = serializers.CharField(source="academic_year.code", read_only=True)

    def to_internal_value(self, data):
        # Garante que deleted_at exista para evitar erros em modelos soft-delete.
        mutable = data.copy()
        mutable.setdefault("deleted_at", None)
        return super().to_internal_value(mutable)

    def validate(self, attrs):
        # Assegura que deleted_at permaneça presente na validação.
        attrs.setdefault("deleted_at", None)
        return super().validate(attrs)

    class Meta:
        # Modelo de origem.
        model = AssessmentPeriod
        # Serializa todos os campos.
        fields = "__all__"


class AssessmentComponentSerializer(serializers.ModelSerializer):
    """Serializer para componentes avaliativos com campos derivados para listagens."""

    # Nome do período associado.
    period_name = serializers.CharField(source="period.name", read_only=True)
    # Nome da disciplina.
    subject_name = serializers.CharField(source="grade_subject.subject.name", read_only=True)
    # Número da classe.
    grade_number = serializers.IntegerField(source="grade_subject.grade.number", read_only=True)
    # Código do ano letivo.
    academic_year_code = serializers.CharField(source="grade_subject.academic_year.code", read_only=True)

    def to_internal_value(self, data):
        # Preenche deleted_at para operações de escrita.
        mutable = data.copy()
        mutable.setdefault("deleted_at", None)
        return super().to_internal_value(mutable)

    class Meta:
        # Modelo de origem.
        model = AssessmentComponent
        # Serializa todos os campos.
        fields = "__all__"


class AssessmentOutcomeMapSerializer(serializers.ModelSerializer):
    """Serializer para mapeamentos de componente para resultado."""

    # Nome do componente (read-only).
    component_name = serializers.CharField(source="component.name", read_only=True)
    # Código do resultado.
    outcome_code = serializers.CharField(source="outcome.code", read_only=True)
    # Descrição do resultado.
    outcome_description = serializers.CharField(source="outcome.description", read_only=True)

    class Meta:
        # Modelo de origem.
        model = AssessmentOutcomeMap
        # Serializa todos os campos.
        fields = "__all__"


class AssessmentSerializer(serializers.ModelSerializer):
    """Serializer completo da avaliação com campos derivados para exibição."""

    # Nome do aluno.
    student_name = serializers.CharField(source="student.name", read_only=True)
    # Nome da competência.
    competency_name = serializers.CharField(source="competency.name", read_only=True)
    # Nome do professor.
    teacher_name = serializers.CharField(source="teaching_assignment.teacher.name", read_only=True)
    # Nome da turma.
    classroom_name = serializers.CharField(source="teaching_assignment.classroom.name", read_only=True)
    # Nome da disciplina.
    subject_name = serializers.CharField(source="teaching_assignment.grade_subject.subject.name", read_only=True)
    # Código do ano letivo.
    academic_year_code = serializers.CharField(source="teaching_assignment.classroom.academic_year.code", read_only=True)
    # Número da classe.
    grade_number = serializers.IntegerField(source="teaching_assignment.classroom.grade.number", read_only=True)
    # Nome do período.
    period_name = serializers.CharField(source="period.name", read_only=True)
    # Nome do componente.
    component_name = serializers.CharField(source="component.name", read_only=True)

    class Meta:
        # Modelo de origem.
        model = Assessment
        # Serializa todos os campos.
        fields = "__all__"


class SubjectPeriodResultSerializer(serializers.ModelSerializer):
    """Serializer de resultados agregados por período e disciplina."""

    # Nome do aluno.
    student_name = serializers.CharField(source="student.name", read_only=True)
    # Nome do professor.
    teacher_name = serializers.CharField(source="teaching_assignment.teacher.name", read_only=True)
    # Nome da turma.
    classroom_name = serializers.CharField(source="teaching_assignment.classroom.name", read_only=True)
    # Nome da disciplina.
    subject_name = serializers.CharField(source="teaching_assignment.grade_subject.subject.name", read_only=True)
    # Nome do período.
    period_name = serializers.CharField(source="period.name", read_only=True)

    class Meta:
        # Modelo de origem.
        model = SubjectPeriodResult
        # Serializa todos os campos.
        fields = "__all__"
