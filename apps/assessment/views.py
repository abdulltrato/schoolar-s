from datetime import date
# Lida com parsing de datas vindas da requisição.

from rest_framework import status
# Constantes de status HTTP.
from rest_framework.decorators import action
# Permite adicionar ações customizadas aos viewsets.
from rest_framework.response import Response
# Respostas HTTP do DRF.

from core.viewsets import RobustModelViewSet
# ViewSet base com tratamento robusto de erros e auditoria.
from .scheduler import ScheduleError, schedule_assessments
# Utilitário de agendamento e exceção específica.

from .models import Assessment, AssessmentComponent, AssessmentOutcomeMap, AssessmentPeriod, SubjectPeriodResult
# Modelos expostos via API.
from .serializers import (
    AssessmentComponentSerializer,
    AssessmentOutcomeMapSerializer,
    AssessmentPeriodSerializer,
    AssessmentSerializer,
    SubjectPeriodResultSerializer,
)
# Serializers correspondentes aos modelos.


class AssessmentPeriodViewSet(RobustModelViewSet):
    """CRUD de períodos avaliativos com filtros e ordenação padrão."""

    # Consulta padrão inclui ano letivo relacionado.
    queryset = AssessmentPeriod.objects.select_related("academic_year").all()
    # Serializer utilizado.
    serializer_class = AssessmentPeriodSerializer
    # Campos pesquisáveis.
    search_fields = ("name", "academic_year__code")
    # Campos de ordenação permitidos.
    ordering_fields = ("id", "academic_year__code", "order", "name")
    # Ordenação padrão.
    ordering = ("academic_year__code", "order")
    # Controle de papéis autorizados por ação.
    allowed_roles = {
        "*": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher"},
        "list": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher", "student", "guardian"},
        "retrieve": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher", "student", "guardian"},
    }


class AssessmentComponentViewSet(RobustModelViewSet):
    """CRUD de componentes avaliativos, trazendo relacionamentos essenciais."""

    # Inclui período, ano letivo, classe e disciplina na consulta.
    queryset = AssessmentComponent.objects.select_related(
        "period",
        "period__academic_year",
        "grade_subject",
        "grade_subject__grade",
        "grade_subject__subject",
    ).all()
    serializer_class = AssessmentComponentSerializer
    # Campos permitidos para busca.
    search_fields = ("name", "type", "period__name", "grade_subject__subject__name")
    # Campos permitidos para ordenação.
    ordering_fields = ("id", "period__order", "grade_subject__subject__name", "name", "weight")
    # Ordenação padrão.
    ordering = ("period__academic_year__code", "period__order", "grade_subject__subject__name")
    # Reutiliza permissões do viewset de períodos.
    allowed_roles = AssessmentPeriodViewSet.allowed_roles


class AssessmentOutcomeMapViewSet(RobustModelViewSet):
    """CRUD de mapeamentos entre componentes e resultados de aprendizagem."""

    # Inclui relações de componente e resultado.
    queryset = AssessmentOutcomeMap.objects.select_related(
        "component",
        "component__grade_subject",
        "component__grade_subject__subject",
        "outcome",
    ).all()
    serializer_class = AssessmentOutcomeMapSerializer
    # Campos de pesquisa.
    search_fields = ("component__name", "outcome__code", "outcome__description", "tenant_id")
    # Campos de ordenação.
    ordering_fields = ("id", "weight", "tenant_id")
    # Ordenação padrão (peso decrescente).
    ordering = ("-weight",)
    # Permissões herdadas.
    allowed_roles = AssessmentPeriodViewSet.allowed_roles


class AssessmentViewSet(RobustModelViewSet):
    """CRUD de avaliações individuais, com agregação de dados de turma e disciplina."""

    # Consulta padrão inclui todas as FKs necessárias para listagens ricas.
    queryset = Assessment.objects.select_related(
        "student",
        "competency",
        "period",
        "component",
        "teaching_assignment",
        "teaching_assignment__teacher",
        "teaching_assignment__classroom",
        "teaching_assignment__classroom__academic_year",
        "teaching_assignment__classroom__grade",
        "teaching_assignment__grade_subject",
        "teaching_assignment__grade_subject__subject",
    ).all()
    # Serializer associado.
    serializer_class = AssessmentSerializer
    # Campos pesquisáveis na API.
    search_fields = (
        "student__name",
        "tenant_id",
        "competency__name",
        "type",
        "period__name",
        "component__name",
        "teaching_assignment__grade_subject__subject__name",
        "teaching_assignment__classroom__name",
    )
    # Campos permitidos para ordenação.
    ordering_fields = ("id", "tenant_id", "date", "type", "student__name", "teaching_assignment__classroom__name", "period__order")
    # Ordenação padrão (mais recentes primeiro).
    ordering = ("-date",)
    # Identificador usado na camada de auditoria.
    audit_resource = "assessment"
    # Papéis autorizados por ação.
    allowed_roles = {
        "*": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher"},
        "list": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher", "student", "guardian"},
        "retrieve": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher", "student", "guardian"},
    }

    @action(methods=["post"], detail=False, url_path="agendar")
    def agendar(self, request):
        """
        Agenda avaliações/exames para uma turma inteira, seleção ou aluno único.
        Considera automaticamente as taxas de exame ao criar avaliações do tipo exame.
        """
        # Extrai payload da requisição.
        data = request.data or {}
        try:
            # Converte data ISO para objeto date.
            raw_date = data.get("date")
            if raw_date:
                parsed_date = date.fromisoformat(raw_date)
            else:
                raise ScheduleError("O campo date é obrigatório (YYYY-MM-DD).")
            # Chama serviço de agendamento.
            created = schedule_assessments(
                teaching_assignment_id=data.get("teaching_assignment"),
                component_id=data.get("component"),
                date_avaliacao=parsed_date,
                target=data.get("target", "turma"),
                student_ids=data.get("student_ids") or [],
                exam_tipo=data.get("exam_tipo", "exam_regular"),
            )
        except ScheduleError as exc:
            # Responde com erro de validação amigável.
            return Response({"erro": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        # Retorna quantidade criada.
        return Response({"criados": created}, status=status.HTTP_201_CREATED)


class SubjectPeriodResultViewSet(RobustModelViewSet):
    """CRUD de resultados agregados por período e disciplina."""

    # Consulta padrão inclui relacionamentos para exibição.
    queryset = SubjectPeriodResult.objects.select_related(
        "student",
        "period",
        "period__academic_year",
        "teaching_assignment",
        "teaching_assignment__teacher",
        "teaching_assignment__classroom",
        "teaching_assignment__grade_subject",
        "teaching_assignment__grade_subject__subject",
    ).all()
    serializer_class = SubjectPeriodResultSerializer
    # Campos pesquisáveis.
    search_fields = ("student__name", "period__name", "teaching_assignment__grade_subject__subject__name")
    # Campos de ordenação permitidos.
    ordering_fields = ("id", "final_average", "period__order", "student__name")
    # Ordenação padrão.
    ordering = ("period__academic_year__code", "period__order", "student__name")
    # Papéis autorizados.
    allowed_roles = {
        "*": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher"},
        "list": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher", "student", "guardian"},
        "retrieve": {"national_admin", "provincial_admin", "district_admin", "school_director", "teacher", "student", "guardian"},
    }
