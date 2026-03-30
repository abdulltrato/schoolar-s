from django.db import transaction
# Fornece contexto transacional.
from django.utils import timezone
# Utilizado para timestamps de emissão.

from apps.assessment.models import Assessment
# Modelo de avaliação usado para buscar exames.
from apps.learning.models_courses import CourseModule
# Modelo que liga curso a disciplinas.

from .models import Certificate, CertificateExamRecord
# Modelos de certificado e registros de exame.


class CertificateError(Exception):
    """Erro de domínio para falhas ao gerar certificado."""

    pass


# Conjunto de tipos de componente que representam exames finais.
EXAM_COMPONENT_TYPES = {"exam"}


def _collect_course_exam_subjects(course):
    """Lista IDs de disciplinas vinculadas ao curso via módulos."""
    return list(course.modules.values_list("subject_id", flat=True))


def _collect_exam_assessments(student, course):
    """Busca avaliações de exame do aluno nas disciplinas do curso."""
    # Obtém disciplinas relacionadas ao curso.
    subject_ids = _collect_course_exam_subjects(course)
    # Se não houver disciplinas, retorna queryset vazio.
    if not subject_ids:
        return Assessment.objects.none()
    # Filtra avaliações do aluno que sejam exames e pertençam às disciplinas do curso.
    return (
        Assessment.objects.filter(
            student=student,
            deleted_at__isnull=True,
            component__grade_subject__subject_id__in=subject_ids,
            component__type__in=EXAM_COMPONENT_TYPES,
        )
        .select_related(
            "component",
            "component__grade_subject",
            "component__grade_subject__subject",
        )
        .order_by("date")
    )


def create_certificate(student, course, *, notes=""):
    """Cria certificado emitido com registros de exames do aluno para o curso."""
    # Busca avaliações relevantes.
    assessments = _collect_exam_assessments(student, course)
    # Garante que existam exames.
    if not assessments.exists():
        raise CertificateError("Nenhum exame encontrado para o curso e aluno informados.")

    record_payloads = []
    # Constrói payloads de registros de exame a partir das avaliações.
    for assessment in assessments:
        subject = (
            assessment.component.grade_subject.subject
            if assessment.component and assessment.component.grade_subject
            else None
        )
        # Ignora avaliações sem disciplina resolvida.
        if not subject:
            continue
        # Ignora avaliações sem nota lançada.
        if assessment.score is None:
            continue
        record_payloads.append(
            {
                "assessment": assessment,
                "subject": subject,
                "exam_type": assessment.type or assessment.component.type,
                "score": assessment.score,
                "exam_date": assessment.date,
            }
        )

    # Se nenhum registro válido foi montado, aborta.
    if not record_payloads:
        raise CertificateError("Nenhum exame válido foi encontrado.")

    # Cria certificado e registros em transação atômica.
    with transaction.atomic():
        certificate = Certificate.objects.create(
            student=student,
            course=course,
            status="issued",
            issued_at=timezone.now(),
            notes=notes or "",
        )
        # Prepara instâncias em memória para insert em lote.
        records = [
            CertificateExamRecord(certificate=certificate, **payload) for payload in record_payloads
        ]
        # Insere todos os registros de exame.
        CertificateExamRecord.objects.bulk_create(records)
        return certificate
