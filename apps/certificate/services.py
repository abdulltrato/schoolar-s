from django.db import transaction
from django.utils import timezone

from apps.assessment.models import Assessment
from apps.learning.models_courses import CourseModule

from .models import Certificate, CertificateExamRecord


class CertificateError(Exception):
    pass


EXAM_COMPONENT_TYPES = {"exam"}


def _collect_course_exam_subjects(course):
    return list(course.modules.values_list("subject_id", flat=True))


def _collect_exam_assessments(student, course):
    subject_ids = _collect_course_exam_subjects(course)
    if not subject_ids:
        return Assessment.objects.none()
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
    assessments = _collect_exam_assessments(student, course)
    if not assessments.exists():
        raise CertificateError("Nenhum exame encontrado para o curso e aluno informados.")

    record_payloads = []
    for assessment in assessments:
        subject = (
            assessment.component.grade_subject.subject
            if assessment.component and assessment.component.grade_subject
            else None
        )
        if not subject:
            continue
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

    if not record_payloads:
        raise CertificateError("Nenhum exame válido foi encontrado.")

    with transaction.atomic():
        certificate = Certificate.objects.create(
            student=student,
            course=course,
            status="issued",
            issued_at=timezone.now(),
            notes=notes or "",
        )
        records = [
            CertificateExamRecord(certificate=certificate, **payload) for payload in record_payloads
        ]
        CertificateExamRecord.objects.bulk_create(records)
        return certificate
