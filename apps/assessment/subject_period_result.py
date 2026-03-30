from decimal import Decimal
# Utiliza decimais para manter precisão das médias.

from django.core.exceptions import ValidationError
# Importa exceção de validação.
from django.db import models
# Importa campos e utilidades do ORM.

from core.models import BaseCodeModel
# Modelo base com suporte a tenant e códigos.
from .assessment import Assessment
# Modelo de avaliação, usado para agregação.
from .period import AssessmentPeriod
# Modelo de período avaliativo referenciado.


class SubjectPeriodResult(BaseCodeModel):
    """Resultado agregado de um estudante em uma disciplina dentro de um período avaliativo."""

    # Prefixo para geração automática de código.
    CODE_PREFIX = "SPR"

    # Estudante avaliado.
    student = models.ForeignKey("academic.Student", on_delete=models.CASCADE, verbose_name="Aluno")
    # Alocação docente (turma/disciplina) vinculada.
    teaching_assignment = models.ForeignKey("school.TeachingAssignment", on_delete=models.CASCADE, verbose_name="Alocação docente")
    # Período avaliativo.
    period = models.ForeignKey(AssessmentPeriod, on_delete=models.CASCADE, verbose_name="Período")
    # Média final ponderada no período.
    final_average = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Média final")
    # Número de avaliações consideradas no cálculo.
    assessments_counted = models.PositiveSmallIntegerField(default=0, verbose_name="Avaliações consideradas")

    @classmethod
    def recalculate(cls, *, student, teaching_assignment, period):
        """Recalcula a média ponderada do aluno para a disciplina no período informado."""
        # Busca avaliações válidas com nota e componente associado.
        assessments = Assessment.objects.filter(
            student=student,
            teaching_assignment=teaching_assignment,
            period=period,
            component__isnull=False,
            score__isnull=False,
        ).select_related("component")

        # Inicializa acumuladores de peso e nota ponderada.
        total_weight = Decimal("0")
        weighted_total = Decimal("0")

        # Percorre cada avaliação para somar notas normalizadas.
        for assessment in assessments:
            weight = Decimal(assessment.component.weight)
            max_score = Decimal(assessment.component.max_score)
            score = Decimal(assessment.score)
            normalized_score = (score / max_score) * Decimal("20")
            weighted_total += normalized_score * weight
            total_weight += weight

        # Conta avaliações e verifica se há pesos suficientes.
        total_assessments = assessments.count()
        if total_weight <= 0 or total_assessments == 0:
            # Sem dados válidos, remove resultado existente.
            cls.objects.filter(
                student=student,
                teaching_assignment=teaching_assignment,
                period=period,
            ).delete()
            return None

        # Calcula média final ponderada.
        final_average = weighted_total / total_weight

        # Tenta herdar tenant de qualquer relação disponível.
        tenant_id = (getattr(student, "tenant_id", "") or getattr(teaching_assignment, "tenant_id", "") or getattr(period, "tenant_id", "") or "").strip()
        # Atualiza ou cria registro mesmo se estiver soft-deletado.
        result, _ = cls.all_objects.update_or_create(
            student=student,
            teaching_assignment=teaching_assignment,
            period=period,
            defaults={
                "tenant_id": tenant_id,
                "final_average": final_average.quantize(Decimal("0.01")),
                "assessments_counted": total_assessments,
                "deleted_at": None,
            },
        )
        return result

    @classmethod
    def recalcular(cls, *, student, teaching_assignment, period):
        """Alias em português para recalculate, mantendo compatibilidade com código legado."""
        return cls.recalculate(
            student=student,
            teaching_assignment=teaching_assignment,
            period=period,
        )

    def clean(self):
        """Valida consistência de tenant e vínculos com turma/período."""
        # Captura tenants das entidades relacionadas.
        student_tenant = (self.student.tenant_id or "").strip() if self.student_id else ""
        assignment_tenant = (self.teaching_assignment.tenant_id or "").strip() if self.teaching_assignment_id else ""
        period_tenant = (self.period.tenant_id or "").strip() if self.period_id else ""
        # Garante que tenant do resultado combine com todos os relacionados.
        for related_tenant in [student_tenant, assignment_tenant, period_tenant]:
            if self.tenant_id and related_tenant and self.tenant_id != related_tenant:
                raise ValidationError({"tenant_id": "Result tenant must match related records."})
        # Confere consistência entre aluno e alocação.
        if student_tenant and assignment_tenant and student_tenant != assignment_tenant:
            raise ValidationError({"tenant_id": "Student and teaching assignment must belong to the same tenant."})
        # Confere consistência entre período e alocação.
        if period_tenant and assignment_tenant and period_tenant != assignment_tenant:
            raise ValidationError({"tenant_id": "Period and teaching assignment must belong to the same tenant."})
        # Preenche tenant herdado.
        self.tenant_id = self.tenant_id or student_tenant or assignment_tenant or period_tenant
        if not (self.tenant_id or "").strip():
            raise ValidationError({"tenant_id": "tenant_id is required."})
        # Valida se período pertence ao mesmo ano letivo da turma.
        if self.period.academic_year_id != self.teaching_assignment.classroom.academic_year_id:
            raise ValidationError({"period": "The period must belong to the same academic year as the teaching assignment."})
        # Garante que aluno pertence à turma em ciclo e classe.
        if self.student.cycle != self.teaching_assignment.classroom.cycle or self.student.grade != self.teaching_assignment.classroom.grade.number:
            raise ValidationError({"student": "The student must belong to the teaching assignment classroom."})

    def save(self, *args, **kwargs):
        # Executa validações antes de salvar.
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        # Representação amigável do resultado.
        return f"Result {self.student} - {self.teaching_assignment.grade_subject.subject} - {self.period}"

    class Meta:
        # Rótulos no admin.
        verbose_name = "Resultado por período e disciplina"
        verbose_name_plural = "Resultados por período e disciplina"
        # Ordenação padrão.
        ordering = ["period__academic_year__code", "period__order", "student__name"]
        # Garante unicidade ativa por aluno + disciplina + período.
        constraints = [
            models.UniqueConstraint(
                fields=["student", "teaching_assignment", "period"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_subject_period_result_active",
            ),
        ]
