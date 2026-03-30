from core.viewsets import RobustModelViewSet

# Importa os modelos necessários para construir os viewsets.
from .models import Guardian, Student, StudentGuardian, StudentOutcome
# Importa os serializers que definem a apresentação dos modelos.
from .serializers import (
    GuardianSerializer,
    StudentGuardianSerializer,
    StudentOutcomeSerializer,
    StudentSerializer,
)


# ViewSet que expõe CRUD de alunos com filtros e permissões.
class StudentViewSet(RobustModelViewSet):
    """CRUD de alunos com filtros por trilho/ciclo e controle de papéis."""
    # Consulta base com prefetch para reduzir consultas em séries.
    queryset = Student.objects.prefetch_related(
        "studentcompetency_set__competency",
        "studentoutcome_set__outcome",
    ).all()
    # Serializer usado para entrada/saída.
    serializer_class = StudentSerializer
    # Campos habilitados para busca textual.
    search_fields = ("name", "estado", "tenant_id")
    # Campos permitidos para ordenação via querystring.
    ordering_fields = (
        "id",
        "name",
        "tenant_id",
        "grade",
        "cycle",
        "cycle_model__code",
        "education_path",
        "birth_date",
    )
    # Ordenação padrão por nome.
    ordering = ("name",)
    # Mapa de papéis autorizados por ação.
    allowed_roles = {
        "*": {
            "national_admin",
            "provincial_admin",
            "district_admin",
            "school_director",
        },
        "list": {
            "national_admin",
            "provincial_admin",
            "district_admin",
            "school_director",
            "teacher",
            "student",
            "guardian",
        },
        "retrieve": {
            "national_admin",
            "provincial_admin",
            "district_admin",
            "school_director",
            "teacher",
            "student",
            "guardian",
        },
    }

    @staticmethod
    def _apply_track_filters(queryset, params):
        # Lê parâmetro de ramo de ensino e normaliza.
        track = (params.get("track") or params.get("education_track") or "").lower()
        # Filtra alunos do ensino geral (até 12ª classe).
        if track in {"general", "geral"}:
            queryset = queryset.filter(grade__lte=12)
        # Filtra alunos do ensino técnico (13ª em diante).
        elif track in {"technical", "tecnico", "technical_professional"}:
            queryset = queryset.filter(grade__gte=13)
        # Filtra por código de modelo de ciclo, se enviado.
        cycle_code = (params.get("cycle_model") or "").strip()
        if cycle_code:
            queryset = queryset.filter(cycle_model__code=cycle_code)
        # Retorna queryset possivelmente filtrado.
        return queryset

    def get_queryset(self):
        # Começa do queryset padrão que aplica regras do mixin.
        queryset = super().get_queryset()
        # Aplica filtros de ramo/ciclo baseados nos parâmetros da requisição.
        return self._apply_track_filters(queryset, self.request.query_params)


# ViewSet para encarregados.
class GuardianViewSet(RobustModelViewSet):
    """CRUD de encarregados (guardians) com busca por contatos."""
    # Consulta base simples.
    queryset = Guardian.objects.all()
    # Serializer usado.
    serializer_class = GuardianSerializer
    # Campos pesquisáveis.
    search_fields = ("name", "tenant_id", "phone", "email", "relationship")
    # Campos ordenáveis.
    ordering_fields = ("id", "name", "tenant_id", "relationship", "active")
    # Ordenação padrão.
    ordering = ("name",)
    # Permissões por ação.
    allowed_roles = {
        "*": {
            "national_admin",
            "provincial_admin",
            "district_admin",
            "school_director",
        },
        "list": {
            "national_admin",
            "provincial_admin",
            "district_admin",
            "school_director",
            "teacher",
            "guardian",
        },
        "retrieve": {
            "national_admin",
            "provincial_admin",
            "district_admin",
            "school_director",
            "teacher",
            "guardian",
        },
    }


# ViewSet para vínculo aluno-encarregado.
class StudentGuardianViewSet(RobustModelViewSet):
    """CRUD de relações aluno-encarregado."""
    # Usa select_related para reduzir consultas nas FK.
    queryset = StudentGuardian.objects.select_related("student", "guardian").all()
    # Serializer correspondente.
    serializer_class = StudentGuardianSerializer
    # Campos pesquisáveis via lookup aninhado.
    search_fields = ("student__name", "guardian__name")
    # Campos permitidos para ordenação.
    ordering_fields = ("id", "student__name", "guardian__name", "primary_contact")
    # Ordenação padrão.
    ordering = ("student__name", "guardian__name")
    # Mapa de papéis autorizados.
    allowed_roles = {
        "*": {
            "national_admin",
            "provincial_admin",
            "district_admin",
            "school_director",
        },
        "list": {
            "national_admin",
            "provincial_admin",
            "district_admin",
            "school_director",
            "teacher",
            "guardian",
        },
        "retrieve": {
            "national_admin",
            "provincial_admin",
            "district_admin",
            "school_director",
            "teacher",
            "guardian",
        },
    }


# ViewSet para resultados de aprendizagem dos alunos.
class StudentOutcomeViewSet(RobustModelViewSet):
    # Usa select_related para pegar aluno e resultado numa consulta.
    queryset = StudentOutcome.objects.select_related("student", "outcome").all()
    # Serializer correspondente.
    serializer_class = StudentOutcomeSerializer
    # Campos pesquisáveis (incluindo atributos do outcome).
    search_fields = (
        "student__name",
        "outcome__code",
        "outcome__description",
        "tenant_id",
    )
    # Campos permitidos para ordenação.
    ordering_fields = ("id", "updated_at", "mastery_level", "evidence_count")
    # Ordenação padrão mais recente primeiro.
    ordering = ("-updated_at",)
    # Mapa de papéis autorizados.
    allowed_roles = {
        "*": {
            "national_admin",
            "provincial_admin",
            "district_admin",
            "school_director",
        },
        "list": {
            "national_admin",
            "provincial_admin",
            "district_admin",
            "school_director",
            "teacher",
            "student",
            "guardian",
        },
        "retrieve": {
            "national_admin",
            "provincial_admin",
            "district_admin",
            "school_director",
            "teacher",
            "student",
            "guardian",
        },
    }
