from datetime import date
from typing import Iterable, List, Tuple

from django.db import transaction
from django.utils.crypto import get_random_string

from apps.school.models import Enrollment, Invoice, PaymentPlan, TeachingAssignment
from .assessment import Assessment
from .component import AssessmentComponent
from .question_service import assign_questions_to_assessment


class ScheduleError(ValueError):
    """Erro de validação ao agendar avaliações/exames."""


ALLOWED_TARGETS = {"turma", "selecionados", "individual"}
ALLOWED_EXAMS = {"exam_regular", "exam_recurrence", "exam_special"}


def _resolve_students(teaching_assignment: TeachingAssignment, target: str, student_ids: Iterable[int]) -> List[int]:
    if target not in ALLOWED_TARGETS:
        raise ScheduleError("O campo target deve ser turma, selecionados ou individual.")
    enrolled_ids = list(
        Enrollment.objects.filter(classroom=teaching_assignment.classroom)
        .values_list("student_id", flat=True)
        .distinct()
    )
    enrolled_set = set(enrolled_ids)

    if target == "turma":
        return enrolled_ids

    requested = {int(sid) for sid in student_ids or []}
    if not requested:
        raise ScheduleError("Forneça os estudantes quando o alvo não é a turma inteira.")
    invalid = requested.difference(enrolled_set)
    if invalid:
        raise ScheduleError("Todos os estudantes devem estar matriculados na turma selecionada.")
    if target == "individual" and len(requested) != 1:
        raise ScheduleError("Selecione apenas um estudante para alvo individual.")
    return list(requested)


def _exam_fee_for(enrollment: Enrollment, plan_type: str):
    if plan_type == "exam_regular":
        return enrollment.exam_fee
    if plan_type == "exam_recurrence":
        return enrollment.exam_recurrence_fee
    if plan_type == "exam_special":
        return enrollment.exam_special_fee
    return 0


def _issue_exam_invoice(enrollment: Enrollment, plan_type: str, due: date) -> Tuple[Invoice, PaymentPlan]:
    amount = _exam_fee_for(enrollment, plan_type)
    if not amount or amount <= 0:
        raise ScheduleError("A matrícula não possui taxa configurada para este exame.")

    plan, _ = PaymentPlan.objects.get_or_create(
        enrollment=enrollment,
        student=enrollment.student,
        school=enrollment.classroom.school,
        tenant_id=enrollment.tenant_id,
        type=plan_type,
        defaults={
            "description": plan_type.replace("_", " ").title(),
            "amount": amount,
            "due_date": due,
            "status": "scheduled",
        },
    )

    if plan.invoice_id:
        return plan.invoice, plan

    reference = f"EXA-{enrollment.code}-{plan_type[:3].upper()}-{get_random_string(5)}"
    invoice = Invoice.objects.create(
        tenant_id=enrollment.tenant_id,
        student=enrollment.student,
        school=enrollment.classroom.school,
        reference=reference,
        description=f"Taxa de {plan.get_type_display()}",
        amount=plan.amount,
        due_date=due,
        status="draft",
    )
    plan.invoice = invoice
    plan.status = "invoiced"
    plan.due_date = plan.due_date or due
    plan.save(update_fields=["invoice", "status", "due_date", "updated_at"])
    return invoice, plan


@transaction.atomic
def schedule_assessments(
    *,
    teaching_assignment_id: int,
    component_id: int,
    date_avaliacao: date,
    target: str,
    student_ids: Iterable[int] = None,
    exam_tipo: str = "exam_regular",
) -> int:
    """
    Cria avaliações para a turma inteira, subset ou aluno único.
    Se o componente for do tipo 'exam', gera também fatura e plano de pagamento correspondente.
    Retorna a quantidade de avaliações criadas.
    """

    if exam_tipo not in ALLOWED_EXAMS:
        raise ScheduleError("exam_tipo deve ser exam_regular, exam_recurrence ou exam_special.")

    teaching_assignment = TeachingAssignment.objects.select_related("classroom", "grade_subject").get(
        pk=teaching_assignment_id
    )
    component = AssessmentComponent.objects.select_related("period", "grade_subject").get(pk=component_id)

    if component.grade_subject_id != teaching_assignment.grade_subject_id:
        raise ScheduleError("O componente deve pertencer à mesma disciplina da turma.")

    students = _resolve_students(teaching_assignment, target, student_ids)
    created = 0

    for student_id in students:
        # Evita duplicar avaliação na mesma data para o mesmo estudante/componente.
        exists = Assessment.objects.filter(
            student_id=student_id,
            teaching_assignment=teaching_assignment,
            component=component,
            date=date_avaliacao,
            deleted_at__isnull=True,
        ).exists()
        if exists:
            continue

        assessment = Assessment.objects.create(
            tenant_id=teaching_assignment.tenant_id,
            student_id=student_id,
            teaching_assignment=teaching_assignment,
            period=component.period,
            component=component,
            type=component.type,
            date=date_avaliacao,
        )
        assign_questions_to_assessment(assessment)
        created += 1

        if component.type == "exam":
            enrollment = (
                Enrollment.objects.filter(student_id=student_id, classroom=teaching_assignment.classroom)
                .select_related("classroom")
                .first()
            )
            if enrollment:
                _issue_exam_invoice(enrollment, exam_tipo, date_avaliacao)

    return created
