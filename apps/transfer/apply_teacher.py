from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from core.request_context import suspend_current_request


def apply_teacher_transfer(transfer, *, actor):
    """
    Executa a transferência de professor. Espera instância validada.
    """
    from apps.learning.models import CourseOffering
    from apps.school.models import Classroom, ManagementAssignment, TeachingAssignment, Teacher, UserProfile

    now = timezone.now()
    with transaction.atomic(), suspend_current_request():
        teacher = Teacher.objects.select_for_update().get(pk=transfer.teacher_id)
        to_school = transfer.to_school or (transfer.to_classroom.school if transfer.to_classroom_id else None)
        if not to_school:
            raise ValidationError({"to_school": "Informe a escola de destino."})

        target_tenant = (to_school.tenant_id or "").strip()
        source_tenant = (teacher.tenant_id or "").strip()
        if not target_tenant:
            raise ValidationError({"to_school": "A escola de destino não possui tenant_id."})

        if teacher.user_id:
            profile, _ = UserProfile.all_objects.get_or_create(user=teacher.user, defaults={"role": "teacher"})
            profile.role = "teacher"
            profile.school = to_school
            profile.tenant_id = target_tenant
            if actor is not None and hasattr(profile, "usuario_id"):
                profile.usuario = actor
            profile.deleted_at = None
            profile.save()

        if target_tenant != source_tenant:
            current_specialty_tenant = (getattr(getattr(teacher, "specialty", None), "tenant_id", "") or "").strip()
            new_specialty_tenant = (getattr(transfer.new_specialty, "tenant_id", "") or "").strip() if transfer.new_specialty_id else ""
            if current_specialty_tenant and current_specialty_tenant != target_tenant:
                if not transfer.new_specialty_id:
                    raise ValidationError({"new_specialty": "Informe a especialidade no tenant de destino."})
                if new_specialty_tenant and new_specialty_tenant != target_tenant:
                    raise ValidationError({"new_specialty": "A nova especialidade deve pertencer ao tenant de destino."})
                teacher.specialty = transfer.new_specialty

            Classroom.objects.filter(
                tenant_id=source_tenant,
                lead_teacher=teacher,
                deleted_at__isnull=True,
            ).update(lead_teacher=None, updated_at=now, usuario=actor if actor else None)

            TeachingAssignment.objects.filter(
                tenant_id=source_tenant,
                teacher=teacher,
                deleted_at__isnull=True,
            ).update(deleted_at=now, updated_at=now, usuario=actor if actor else None)

            ManagementAssignment.objects.filter(
                tenant_id=source_tenant,
                teacher=teacher,
                deleted_at__isnull=True,
            ).update(deleted_at=now, updated_at=now, usuario=actor if actor else None)

            CourseOffering.objects.filter(
                tenant_id=source_tenant,
                teacher=teacher,
                deleted_at__isnull=True,
            ).update(teacher=None, updated_at=now, usuario=actor if actor else None)

        teacher.school = to_school
        teacher.tenant_id = target_tenant
        if transfer.new_specialty_id:
            teacher.specialty = transfer.new_specialty
        if actor is not None and hasattr(teacher, "usuario_id"):
            teacher.usuario = actor
        teacher.save()

        if transfer.to_classroom_id:
            to_classroom = transfer.to_classroom
            if transfer.from_classroom_id:
                from_classroom = transfer.from_classroom
                if getattr(from_classroom, "lead_teacher_id", None) == teacher.id:
                    from_classroom.lead_teacher = None
                    if actor is not None and hasattr(from_classroom, "usuario_id"):
                        from_classroom.usuario = actor
                    from_classroom.save(update_fields=["lead_teacher", "usuario", "updated_at"] if actor is not None else ["lead_teacher", "updated_at"])

            if getattr(to_classroom, "lead_teacher_id", None) not in {None, teacher.id}:
                raise ValidationError({"to_classroom": "A turma de destino já possui diretor de turma."})
            to_classroom.lead_teacher = teacher
            if actor is not None and hasattr(to_classroom, "usuario_id"):
                to_classroom.usuario = actor
            to_classroom.save(update_fields=["lead_teacher", "usuario", "updated_at"] if actor is not None else ["lead_teacher", "updated_at"])

        if transfer.move_teaching_assignments:
            from_classroom = transfer.from_classroom
            to_classroom = transfer.to_classroom
            if from_classroom.academic_year_id != to_classroom.academic_year_id:
                raise ValidationError({"to_classroom": "As turmas devem pertencer ao mesmo ano letivo."})
            if from_classroom.grade_id != to_classroom.grade_id:
                raise ValidationError({"to_classroom": "As turmas devem pertencer à mesma classe."})

            assignments = TeachingAssignment.objects.filter(
                teacher=teacher,
                classroom=from_classroom,
                deleted_at__isnull=True,
            ).select_related("grade_subject")
            for assignment in assignments:
                assignment.classroom = to_classroom
                if actor is not None and hasattr(assignment, "usuario_id"):
                    assignment.usuario = actor
                assignment.save()
