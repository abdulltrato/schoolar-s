from core.viewsets import RobustModelViewSet
# ViewSet base com tratamento robusto de exceções.

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
# Modelos de currículo usados pelas APIs.
from .serializers import (
    BaseCurriculumSerializer,
    CompetencySerializer,
    CompetencyOutcomeSerializer,
    CurriculumAreaSerializer,
    LearningOutcomeSerializer,
    LocalCurriculumSerializer,
    SubjectSpecialtySerializer,
    SubjectCurriculumPlanSerializer,
    SubjectSerializer,
)
# Serializers correspondentes para entrada/saída.


class CurriculumAreaViewSet(RobustModelViewSet):
    """CRUD de áreas curriculares com busca por nome."""

    # Consulta padrão abrange todas as áreas.
    queryset = CurriculumArea.objects.all()
    # Serializer usado para entrada/saída.
    serializer_class = CurriculumAreaSerializer
    # Permite search por nome.
    search_fields = ("name",)
    # Campos permitidos para ordenação.
    ordering_fields = ("id", "name")
    # Ordenação padrão alfabética.
    ordering = ("name",)


class SubjectViewSet(RobustModelViewSet):
    """CRUD de disciplinas, trazendo área relacionada."""

    # Inclui área para evitar N+1.
    queryset = Subject.objects.select_related("area").all()
    # Serializer correspondente.
    serializer_class = SubjectSerializer
    # Busca por nome e área.
    search_fields = ("name", "area__name")
    # Campos liberados para ordenação.
    ordering_fields = ("id", "name", "cycle", "area__name")
    # Ordenação padrão.
    ordering = ("name",)


class SubjectSpecialtyViewSet(RobustModelViewSet):
    """CRUD de especialidades, carregando disciplina associada."""

    # Prefetch da disciplina.
    queryset = SubjectSpecialty.objects.select_related("subject").all()
    # Serializer utilizado.
    serializer_class = SubjectSpecialtySerializer
    # Permite search por especialidade e disciplina.
    search_fields = ("name", "subject__name")
    # Campos ordenáveis.
    ordering_fields = ("id", "name", "subject__name")
    # Ordenação padrão disciplina/nome.
    ordering = ("subject__name", "name")


class CompetencyViewSet(RobustModelViewSet):
    """CRUD de competências com área e disciplina carregadas."""

    # Usa select_related para otimizar acessos.
    queryset = Competency.objects.select_related("area", "subject", "subject__area").all()
    # Serializer correspondente.
    serializer_class = CompetencySerializer
    # Campos de busca.
    search_fields = ("name", "area__name", "subject__name")
    # Campos para ordenação.
    ordering_fields = ("id", "name", "cycle", "area__name")
    # Ordenação padrão.
    ordering = ("name",)


class BaseCurriculumViewSet(RobustModelViewSet):
    """CRUD de currículos base com competências pré-carregadas."""

    # Prefetch para reduzir queries em M2M.
    queryset = BaseCurriculum.objects.prefetch_related("competencies").all()
    # Serializer correspondente.
    serializer_class = BaseCurriculumSerializer
    # Campos ordenáveis.
    ordering_fields = ("id", "cycle")
    # Ordenação padrão por ciclo.
    ordering = ("cycle",)


class LocalCurriculumViewSet(RobustModelViewSet):
    """CRUD de currículos locais com competências adicionais."""

    # Carrega competências extras antecipadamente.
    queryset = LocalCurriculum.objects.prefetch_related("additional_competencies").all()
    # Serializer aplicado.
    serializer_class = LocalCurriculumSerializer
    # Permite pesquisar por tenant.
    search_fields = ("tenant_id",)
    # Campos para ordenação.
    ordering_fields = ("id", "tenant_id", "cycle")
    # Ordenação padrão por tenant e ciclo.
    ordering = ("tenant_id", "cycle")


class SubjectCurriculumPlanViewSet(RobustModelViewSet):
    """CRUD de planos curriculares por disciplina/classe com prefetchs úteis."""

    # Carrega relacionamentos de grade_subject e competências planejadas.
    queryset = (
        SubjectCurriculumPlan.objects.select_related(
            "grade_subject",
            "grade_subject__academic_year",
            "grade_subject__grade",
            "grade_subject__subject",
        )
        .prefetch_related("planned_competencies")
        .all()
    )
    # Serializer correspondente.
    serializer_class = SubjectCurriculumPlanSerializer
    # Busca por ano letivo, classe ou disciplina.
    search_fields = (
        "grade_subject__academic_year__code",
        "grade_subject__grade__name",
        "grade_subject__subject__name",
    )
    # Campos ordenáveis.
    ordering_fields = (
        "id",
        "grade_subject__academic_year__code",
        "grade_subject__grade__number",
        "grade_subject__subject__name",
    )
    # Ordenação padrão por ano e classe.
    ordering = ("grade_subject__academic_year__code", "grade_subject__grade__number")


class LearningOutcomeViewSet(RobustModelViewSet):
    """CRUD de resultados de aprendizagem, carregando disciplina e classe."""

    # Inclui subject e grade para evitar queries extras.
    queryset = LearningOutcome.objects.select_related("subject", "grade").all()
    # Serializer correspondente.
    serializer_class = LearningOutcomeSerializer
    # Busca por código, descrição, tenant ou disciplina.
    search_fields = ("code", "description", "tenant_id", "subject__name")
    # Campos permitidos na ordenação.
    ordering_fields = ("id", "code", "taxonomy_level", "cycle", "tenant_id")
    # Ordenação padrão por código.
    ordering = ("code",)


class CompetencyOutcomeViewSet(RobustModelViewSet):
    """CRUD de alinhamentos competência-resultado."""

    # Carrega competências e resultados relacionados.
    queryset = CompetencyOutcome.objects.select_related("competency", "outcome").all()
    # Serializer correspondente.
    serializer_class = CompetencyOutcomeSerializer
    # Busca por nomes/códigos e tenant.
    search_fields = ("competency__name", "outcome__code", "tenant_id")
    # Campos ordenáveis.
    ordering_fields = ("id", "weight", "tenant_id")
    # Ordenação padrão decrescente pelo peso.
    ordering = ("-weight",)
