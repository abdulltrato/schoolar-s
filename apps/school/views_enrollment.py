from rest_framework import filters, status
# Filtros de busca e códigos HTTP.
from rest_framework.decorators import action
# Decorador para actions customizadas.
from rest_framework.response import Response
# Respostas DRF.

from django.shortcuts import get_object_or_404
# Helper para 404.

from core.viewsets import RobustModelViewSet
# ViewSet com tratamento robusto de erros.
from .models import AttendanceRecord, Classroom, Enrollment
# Modelos de matrículas, turmas e presença.
from .serializers import AttendanceRecordSerializer, EnrollmentSerializer, EnrollmentSummarySerializer
# Serializers correspondentes.


class EnrollmentViewSet(RobustModelViewSet):
    """CRUD de matrículas; inclui action para matricular vários alunos por turma."""
    queryset = Enrollment.objects.select_related("student", "classroom")
    serializer_class = EnrollmentSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["student__name", "classroom__name", "classroom__academic_year__code"]

    @action(methods=["post"], detail=False, url_path="por-turma")
    def matricular_por_turma(self, request):
        """Cria matrículas em lote para uma turma a partir de student_ids."""
        data = request.data or {}
        classroom_id = data.get("classroom")
        student_ids = data.get("student_ids")
        if not classroom_id or not student_ids:
            return Response(
                {"erro": "Informe a turma e a lista de estudantes."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(student_ids, list):
            return Response(
                {"erro": "student_ids deve ser uma lista de identificadores."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        classroom = get_object_or_404(Classroom, pk=classroom_id)
        tenant_id = self._resolve_tenant_id()

        normalized_ids = []
        seen = set()
        for value in student_ids:
            try:
                student_id = int(value)
            except (TypeError, ValueError):
                return Response(
                    {"erro": "student_ids deve conter apenas números inteiros."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if student_id in seen:
                continue
            seen.add(student_id)
            normalized_ids.append(student_id)

        if not normalized_ids:
            return Response({"erro": "Nenhum estudante válido informado."}, status=status.HTTP_400_BAD_REQUEST)

        created = []
        errors = []
        for student_id in normalized_ids:
            serializer = EnrollmentSerializer(
                data={"student": student_id, "classroom": classroom.id},
                context=self.get_serializer_context(),
            )
            if serializer.is_valid():
                save_kwargs = {}
                if tenant_id:
                    save_kwargs["tenant_id"] = tenant_id
                serializer.save(**save_kwargs)
                created.append(serializer.data)
            else:
                errors.append({"student": student_id, "erros": serializer.errors})

        status_code = status.HTTP_201_CREATED if created else status.HTTP_400_BAD_REQUEST
        return Response(
            {"criados": len(created), "matriculas": created, "erros": errors},
            status=status_code,
        )


class EnrollmentSummaryViewSet(RobustModelViewSet):
    """Lista resumida de matrículas com campos derivados de leitura."""
    queryset = Enrollment.objects.select_related("student", "classroom")
    serializer_class = EnrollmentSummarySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["student__name", "classroom__name", "classroom__academic_year__code"]


class AttendanceRecordViewSet(RobustModelViewSet):
    """CRUD de presenças com joins para aluno e turma."""
    queryset = AttendanceRecord.objects.select_related("enrollment__student", "enrollment__classroom")
    serializer_class = AttendanceRecordSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["enrollment__student__name", "enrollment__classroom__name"]
