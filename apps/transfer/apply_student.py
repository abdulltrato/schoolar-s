from django.core.exceptions import ValidationError
# Exceção de validação.
from django.db import transaction
# Controla atomicidade da operação.
from django.utils import timezone
# Timestamp para soft-delete e criação.

from core.request_context import suspend_current_request
# Context manager para suprimir request atual durante operações internas.


def apply_student_transfer(transfer, *, actor):
    """Executa a transferência de aluno (instância já validada)."""
    from django.contrib.auth import get_user_model
    from apps.academic.models import Student
    from apps.school.models import Enrollment, UserProfile

    now = timezone.now()
    with transaction.atomic(), suspend_current_request():
        student = Student.objects.select_for_update().get(pk=transfer.student_id)
        to_classroom = transfer.to_classroom
        target_tenant = (to_classroom.tenant_id or "").strip()
        source_tenant = (student.tenant_id or "").strip()
        if not target_tenant:
            raise ValidationError({"to_classroom": "A turma de destino não possui tenant_id."})

        if target_tenant == source_tenant:
            # Transferência dentro do mesmo tenant: apenas remaneja vínculos.
            if actor is not None and hasattr(student, "usuario_id"):
                student.usuario = actor
                student.save(update_fields=["usuario"])

            if student.user_id:
                profile = getattr(student.user, "school_profile", None)
                if profile is not None:
                    profile.school = getattr(to_classroom, "school", None)
                    if actor is not None and hasattr(profile, "usuario_id"):
                        profile.usuario = actor
                    profile.save(update_fields=["school", "usuario", "updated_at"] if actor is not None else ["school", "updated_at"])

            Enrollment.objects.filter(
                student=student,
                classroom__academic_year=to_classroom.academic_year,
                deleted_at__isnull=True,
            ).update(deleted_at=now, updated_at=now, usuario=actor if actor else None)

            enrollment = Enrollment(student=student, classroom=to_classroom)
            if actor is not None and hasattr(enrollment, "usuario_id"):
                enrollment.usuario = actor
            enrollment.save()
            return

        # Transferência entre tenants: clona aluno no destino e desassocia o original.
        user = student.user
        if not user:
            raise ValidationError({"student": "A transferência de tenant requer que o aluno tenha um usuário."})

        User = get_user_model()
        if not isinstance(user, User):
            raise ValidationError({"student": "Usuário inválido."})

        profile, _ = UserProfile.all_objects.get_or_create(
            user=user,
            defaults={"role": "student"},
        )
        profile.role = "student"
        profile.school = getattr(to_classroom, "school", None)
        profile.tenant_id = target_tenant
        if actor is not None and hasattr(profile, "usuario_id"):
            profile.usuario = actor
        profile.deleted_at = None
        profile.save()

        student.user = None
        student.estado = "transferido"
        if actor is not None and hasattr(student, "usuario_id"):
            student.usuario = actor
        student.save(update_fields=["user", "estado", "usuario", "updated_at"] if actor is not None else ["user", "estado", "updated_at"])

        new_student = Student(
            user=user,
            name=student.name,
            birth_date=student.birth_date,
            grade=student.grade,
            cycle=student.cycle,
            estado="active",
            tenant_id=target_tenant,
        )
        if actor is not None and hasattr(new_student, "usuario_id"):
            new_student.usuario = actor
        new_student.save()

        enrollment = Enrollment(student=new_student, classroom=to_classroom)
        if actor is not None and hasattr(enrollment, "usuario_id"):
            enrollment.usuario = actor
        enrollment.save()
