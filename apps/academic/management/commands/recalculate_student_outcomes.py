import re

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.academic.models import Student, StudentOutcome
from apps.assessment.models import AssessmentOutcomeMap
from apps.school.models import AcademicYear, Classroom


# Comando de gestão para recalcular resultados de alunos.
class Command(BaseCommand):
    # Descrição exibida em `manage.py help`.
    help = "Recalculate student learning outcomes based on assessment mappings."

    def add_arguments(self, parser):
        # Adiciona argumento opcional para filtrar por tenant.
        parser.add_argument("--tenant-id", help="Filter by tenant id.")
        # Permite recalcular um aluno específico.
        parser.add_argument("--student-id", type=int, help="Recalculate a single student.")
        # Permite recalcular todos os alunos de uma turma.
        parser.add_argument("--classroom-id", type=int, help="Recalculate students in a classroom.")
        # Identifica ano letivo por id ou código.
        parser.add_argument("--academic-year", help="Academic year id or code (YYYY-YYYY).")
        # Restringe a um componente específico.
        parser.add_argument("--component-id", type=int, help="Restrict to a component id.")
        # Restringe a um ou mais resultados específicos.
        parser.add_argument("--outcome-id", type=int, action="append", help="Restrict to outcome id(s).")
        # Modo simulação sem gravar alterações.
        parser.add_argument("--dry-run", action="store_true", help="Show what would change without updating.")
        # Tamanho do lote para iterar alunos.
        parser.add_argument("--batch-size", type=int, default=200, help="Batch size for processing students.")

    def handle(self, *args, **options):
        # Extrai e normaliza parâmetros.
        tenant_id = (options.get("tenant_id") or "").strip()
        student_id = options.get("student_id")
        classroom_id = options.get("classroom_id")
        academic_year = options.get("academic_year")
        component_id = options.get("component_id")
        outcome_ids = options.get("outcome_id") or []
        dry_run = options.get("dry_run")
        batch_size = max(1, options.get("batch_size") or 200)

        # Resolve objeto de ano letivo se parâmetro foi fornecido.
        year = None
        if academic_year:
            year = self._resolve_academic_year(academic_year, tenant_id)

        # Monta queryset de alunos a processar.
        students_qs = self._build_students_queryset(
            tenant_id=tenant_id,
            student_id=student_id,
            classroom_id=classroom_id,
            academic_year=year,
        )
        # Conta quantidade total para feedback.
        total_students = students_qs.count()

        # Monta queryset de mapeamentos outcome/componente.
        mapping_qs = self._build_mapping_queryset(
            tenant_id=tenant_id,
            component_id=component_id,
            outcome_ids=outcome_ids,
            academic_year=year,
            classroom_id=classroom_id,
        )
        # Extrai ids de outcomes distintos a recalcular.
        outcome_ids = list(mapping_qs.values_list("outcome_id", flat=True).distinct())

        # Se não há outcomes relevantes, encerra.
        if not outcome_ids:
            self.stdout.write("No outcome mappings found for the given filters.")
            return

        # Contador de processados.
        processed = 0
        # Executa em transação para permitir dry-run.
        with transaction.atomic():
            # Itera alunos em lotes.
            for student in students_qs.iterator(chunk_size=batch_size):
                # Recalcula outcomes para o aluno.
                StudentOutcome.recalculate_for_outcomes(student=student, outcome_ids=outcome_ids)
                processed += 1

            # Se for simulação, marca rollback.
            if dry_run:
                transaction.set_rollback(True)

        # Exibe resumo da operação.
        self.stdout.write(
            f"Recalculated outcomes for {processed}/{total_students} students "
            f"using {len(outcome_ids)} outcomes. dry_run={dry_run}"
        )

    def _resolve_academic_year(self, value, tenant_id):
        # Normaliza entrada para string.
        value = str(value).strip()
        # Se é numérico, busca por PK.
        if value.isdigit():
            return AcademicYear.objects.filter(pk=int(value)).first()
        # Valida formato de código.
        if not re.fullmatch(r"\d{4}-\d{4}", value):
            raise SystemExit("Invalid academic_year format. Use id or YYYY-YYYY.")

        # Busca pelo código informado.
        queryset = AcademicYear.objects.filter(code=value)
        # Restringe por tenant se fornecido.
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        # Limita a dois resultados para checar ambiguidade.
        matches = list(queryset[:2])
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            raise SystemExit("Academic year code is ambiguous. Provide --tenant-id.")
        raise SystemExit("Academic year not found.")

    def _build_students_queryset(self, *, tenant_id, student_id, classroom_id, academic_year):
        # Define queryset inicial (por aluno ou todos).
        if student_id:
            queryset = Student.objects.filter(pk=student_id)
        else:
            queryset = Student.objects.all()

        # Aplica filtro de tenant se houver.
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)

        # Filtra por turma ou ano letivo, conforme parâmetros.
        if classroom_id:
            queryset = queryset.filter(enrollment__classroom_id=classroom_id).distinct()
        elif academic_year:
            queryset = queryset.filter(enrollment__classroom__academic_year=academic_year).distinct()

        # Retorna queryset final.
        return queryset

    def _build_mapping_queryset(self, *, tenant_id, component_id, outcome_ids, academic_year, classroom_id):
        # Começa de todos os mapeamentos ativos.
        queryset = AssessmentOutcomeMap.objects.filter(active=True)
        # Filtra por tenant se fornecido.
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        # Filtra por componente específico.
        if component_id:
            queryset = queryset.filter(component_id=component_id)
        # Filtra por outcomes específicos.
        if outcome_ids:
            queryset = queryset.filter(outcome_id__in=outcome_ids)
        # Filtra por ano letivo via componente.
        if academic_year:
            queryset = queryset.filter(component__period__academic_year=academic_year)
        # Filtra por turma específica, se presente.
        if classroom_id:
            classroom = Classroom.objects.filter(pk=classroom_id).select_related("academic_year", "grade").first()
            if classroom:
                queryset = queryset.filter(
                    component__grade_subject__grade=classroom.grade,
                    component__grade_subject__academic_year=classroom.academic_year,
                )
        # Retorna queryset construído.
        return queryset
