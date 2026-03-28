from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone

from core.models import BaseCodeModel
from core.request_context import get_current_request, suspend_current_request


class Transfer(BaseCodeModel):
    CODE_PREFIX = "TRF"

    KIND_CHOICES = [
        ("student", "Aluno"),
        ("teacher", "Professor"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pendente"),
        ("applied", "Aplicada"),
        ("failed", "Falhou"),
        ("canceled", "Cancelada"),
    ]

    kind = models.CharField(max_length=20, choices=KIND_CHOICES, verbose_name="Tipo")

    student = models.ForeignKey(
        "academic.Student",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="transfers",
        verbose_name="Aluno",
    )
    teacher = models.ForeignKey(
        "school.Teacher",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="transfers",
        verbose_name="Professor",
    )

    from_school = models.ForeignKey(
        "school.School",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        verbose_name="Escola de origem",
    )
    to_school = models.ForeignKey(
        "school.School",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        verbose_name="Escola de destino",
    )
    from_classroom = models.ForeignKey(
        "school.Classroom",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        verbose_name="Turma de origem",
    )
    to_classroom = models.ForeignKey(
        "school.Classroom",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        verbose_name="Turma de destino",
    )

    new_specialty = models.ForeignKey(
        "curriculum.SubjectSpecialty",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="+",
        verbose_name="Nova especialidade",
    )

    move_teaching_assignments = models.BooleanField(default=False, verbose_name="Mover alocações docentes")
    reason = models.TextField(blank=True, verbose_name="Motivo")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="Estado")
    applied_at = models.DateTimeField(null=True, blank=True, verbose_name="Aplicada em")
    error_message = models.TextField(blank=True, verbose_name="Erro")

    class Meta:
        verbose_name = "Transferência"
        verbose_name_plural = "Transferências"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        subject = self.student or self.teacher
        return f"{self.get_kind_display()} - {subject or self.pk}"

    def _resolve_actor(self):
        request = get_current_request()
        user = getattr(request, "user", None) if request else None
        if user and getattr(user, "is_authenticated", False):
            return user
        return None

    def _resolve_source_tenant(self) -> str:
        if self.kind == "student" and self.student_id:
            return (getattr(self.student, "tenant_id", "") or "").strip()
        if self.kind == "teacher" and self.teacher_id:
            return (getattr(self.teacher, "tenant_id", "") or "").strip()
        return ""

    def _resolve_target_tenant(self) -> str:
        if self.to_classroom_id:
            return (getattr(self.to_classroom, "tenant_id", "") or "").strip()
        if self.to_school_id:
            return (getattr(self.to_school, "tenant_id", "") or "").strip()
        return ""

    def clean(self):
        self.kind = (self.kind or "").strip()
        self.status = (self.status or "").strip() or "pending"

        if self.kind not in {"student", "teacher"}:
            raise ValidationError({"kind": "Tipo inválido."})

        if self.kind == "student":
            if not self.student_id:
                raise ValidationError({"student": "Informe o aluno."})
            if self.teacher_id:
                raise ValidationError({"teacher": "Não pode informar professor numa transferência de aluno."})
            if not self.to_classroom_id:
                raise ValidationError({"to_classroom": "Informe a turma de destino."})

            if self.from_classroom_id and self.from_classroom_id == self.to_classroom_id:
                raise ValidationError({"to_classroom": "A turma de destino deve ser diferente da turma de origem."})

            self.to_school = getattr(self.to_classroom, "school", None)
            if self.from_classroom_id:
                self.from_school = getattr(self.from_classroom, "school", None)

        if self.kind == "teacher":
            if not self.teacher_id:
                raise ValidationError({"teacher": "Informe o professor."})
            if self.student_id:
                raise ValidationError({"student": "Não pode informar aluno numa transferência de professor."})
            if not (self.to_classroom_id or self.to_school_id):
                raise ValidationError({"to_school": "Informe a escola ou a turma de destino."})

            if self.to_classroom_id:
                self.to_school = getattr(self.to_classroom, "school", None)
            if self.from_classroom_id:
                self.from_school = getattr(self.from_classroom, "school", None)

            if self.move_teaching_assignments and not (self.from_classroom_id and self.to_classroom_id):
                raise ValidationError({"move_teaching_assignments": "Informe turma de origem e destino para mover alocações."})

        source_tenant = self._resolve_source_tenant()
        if not source_tenant:
            raise ValidationError({"tenant_id": "Não foi possível determinar o tenant de origem."})

        target_tenant = self._resolve_target_tenant()
        if not target_tenant:
            raise ValidationError({"to_school": "Não foi possível determinar o tenant de destino."})

        if not (self.tenant_id or "").strip():
            self.tenant_id = source_tenant

        # Cross-tenant guardrail: requires admin roles, enforced at the API layer too.
        if target_tenant != source_tenant:
            actor = self._resolve_actor()
            profile = getattr(actor, "school_profile", None) if actor else None
            role = getattr(profile, "role", None) if profile else None
            if role not in {"national_admin", "provincial_admin", "district_admin"}:
                raise ValidationError({"to_school": "A transferência entre tenants requer perfil de administrador."})

        if self.kind == "student" and self.from_classroom_id:
            from apps.school.models import Enrollment

            enrolled = Enrollment.objects.filter(
                student_id=self.student_id,
                classroom_id=self.from_classroom_id,
                deleted_at__isnull=True,
            ).exists()
            if not enrolled:
                raise ValidationError({"from_classroom": "O aluno não está matriculado na turma de origem."})

        if self.kind == "teacher" and self.from_classroom_id:
            current_lead = getattr(self.from_classroom, "lead_teacher_id", None)
            if current_lead and current_lead != self.teacher_id:
                raise ValidationError({"from_classroom": "O professor não é o diretor da turma de origem."})

    def apply(self):
        if self.status != "pending":
            raise ValidationError({"status": "Só é possível aplicar transferências pendentes."})

        actor = self._resolve_actor()
        now = timezone.now()

        with transaction.atomic():
            if self.kind == "student":
                self._apply_student(actor=actor, now=now)
            else:
                self._apply_teacher(actor=actor, now=now)

            self.__class__.objects.filter(pk=self.pk).update(
                status="applied",
                applied_at=now,
                error_message="",
                updated_at=now,
            )
            self.status = "applied"
            self.applied_at = now
            self.error_message = ""

    def _apply_student(self, *, actor, now):
        from django.contrib.auth import get_user_model

        from apps.academic.models import Student
        from apps.school.models import Enrollment, UserProfile

        student = Student.objects.select_for_update().get(pk=self.student_id)
        to_classroom = self.to_classroom
        target_tenant = (to_classroom.tenant_id or "").strip()
        source_tenant = (student.tenant_id or "").strip()
        if not target_tenant:
            raise ValidationError({"to_classroom": "A turma de destino não possui tenant_id."})

        with suspend_current_request():
            # Same-tenant: just move enrollment (soft-delete same academic year enrollments).
            if target_tenant == source_tenant:
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

            # Cross-tenant: clone student record and move the linked user to the new tenant.
            user = student.user
            if not user:
                raise ValidationError({"student": "A transferência de tenant requer que o aluno tenha um usuário."})

            # Ensure user model is the expected type.
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

            # Detach user from the old student to prevent cross-tenant joins leaking data.
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

    def _apply_teacher(self, *, actor, now):
        from apps.learning.models import CourseOffering
        from apps.school.models import Classroom, ManagementAssignment, TeachingAssignment, Teacher, UserProfile

        teacher = Teacher.objects.select_for_update().get(pk=self.teacher_id)
        to_school = self.to_school or (self.to_classroom.school if self.to_classroom_id else None)
        if not to_school:
            raise ValidationError({"to_school": "Informe a escola de destino."})

        target_tenant = (to_school.tenant_id or "").strip()
        source_tenant = (teacher.tenant_id or "").strip()
        if not target_tenant:
            raise ValidationError({"to_school": "A escola de destino não possui tenant_id."})

        with suspend_current_request():
            if teacher.user_id:
                profile, _ = UserProfile.all_objects.get_or_create(user=teacher.user, defaults={"role": "teacher"})
                profile.role = "teacher"
                profile.school = to_school
                profile.tenant_id = target_tenant
                if actor is not None and hasattr(profile, "usuario_id"):
                    profile.usuario = actor
                profile.deleted_at = None
                profile.save()

            # If tenant changes, ensure specialty is compatible.
            if target_tenant != source_tenant:
                current_specialty_tenant = (getattr(getattr(teacher, "specialty", None), "tenant_id", "") or "").strip()
                new_specialty_tenant = (getattr(self.new_specialty, "tenant_id", "") or "").strip() if self.new_specialty_id else ""
                if current_specialty_tenant and current_specialty_tenant != target_tenant:
                    if not self.new_specialty_id:
                        raise ValidationError({"new_specialty": "Informe a especialidade no tenant de destino."})
                    if new_specialty_tenant and new_specialty_tenant != target_tenant:
                        raise ValidationError({"new_specialty": "A nova especialidade deve pertencer ao tenant de destino."})
                    teacher.specialty = self.new_specialty

                # Detach old-tenant relations to prevent cross-tenant joins.
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
            if self.new_specialty_id:
                teacher.specialty = self.new_specialty
            if actor is not None and hasattr(teacher, "usuario_id"):
                teacher.usuario = actor
            teacher.save()

            if self.to_classroom_id:
                to_classroom = self.to_classroom
                if self.from_classroom_id:
                    from_classroom = self.from_classroom
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

            if self.move_teaching_assignments:
                from_classroom = self.from_classroom
                to_classroom = self.to_classroom
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
