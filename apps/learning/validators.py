from __future__ import annotations

from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models


def validate_lesson_conflicts(lesson) -> None:
    """
    Prevent scheduling overlaps for lessons that share the same offering, classroom or teacher.
    """
    if not lesson.offering_id or not lesson.scheduled_at:
        return

    duration = lesson.duration_minutes or 0
    if duration <= 0:
        return

    start = lesson.scheduled_at
    end = start + timedelta(minutes=duration)

    # Base queryset: same tenant, not soft-deleted, exclude self.
    candidates = (
        lesson.__class__.objects.filter(deleted_at__isnull=True)
        .exclude(pk=lesson.pk)
        .filter(tenant_id=lesson.tenant_id)
    )

    # Overlap on offering, classroom, or teacher of the offering.
    classroom_id = getattr(lesson.offering, "classroom_id", None)
    teacher_id = getattr(lesson.offering, "teacher_id", None)

    candidates = candidates.filter(
        models.Q(offering_id=lesson.offering_id)
        | models.Q(offering__classroom_id=classroom_id, offering__classroom_id__isnull=False)
        | models.Q(offering__teacher_id=teacher_id, offering__teacher_id__isnull=False)
    )

    for other in candidates:
        other_end = other.scheduled_at + timedelta(minutes=other.duration_minutes or 0)
        overlap = start < other_end and other.scheduled_at < end
        if overlap:
            conflict_target = []
            if other.offering_id == lesson.offering_id:
                conflict_target.append("oferta")
            if classroom_id and getattr(other.offering, "classroom_id", None) == classroom_id:
                conflict_target.append("turma")
            if teacher_id and getattr(other.offering, "teacher_id", None) == teacher_id:
                conflict_target.append("professor")
            conflict_text = " / ".join(conflict_target) if conflict_target else "agenda"
            raise ValidationError(
                {"scheduled_at": f"Conflito de horário com outra aula ({conflict_text}) às {other.scheduled_at}."}
            )


def validate_offering_conflicts(offering) -> None:
    """
    Prevent date-range overlaps for offerings that share classroom or teacher within the same tenant.
    """
    if not offering.start_date or not offering.end_date:
        return
    if not offering.tenant_id:
        return

    candidates = (
        offering.__class__.objects.filter(deleted_at__isnull=True, tenant_id=offering.tenant_id)
        .exclude(pk=offering.pk)
        .filter(start_date__lte=offering.end_date, end_date__gte=offering.start_date)
    )

    classroom_conflict = None
    teacher_conflict = None

    if offering.classroom_id:
        classroom_conflict = candidates.filter(classroom_id=offering.classroom_id).first()
    if offering.teacher_id:
        teacher_conflict = candidates.filter(teacher_id=offering.teacher_id).first()

    errors = {}
    if classroom_conflict:
        errors["classroom"] = "A turma já possui outra oferta neste intervalo de datas."
    if teacher_conflict:
        errors["teacher"] = "O professor já está alocado a outra oferta neste intervalo de datas."

    if errors:
        raise ValidationError(errors)
