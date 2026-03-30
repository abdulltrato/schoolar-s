from datetime import date
# Manipulação de datas para planos de pagamento.
from decimal import Decimal
# Operações monetárias sem perda de precisão.

from django.contrib.auth import get_user_model
# Modelo de usuário para conectar sinais.
from django.db import connection
# Acesso direto ao DB para limpeza de tabelas legadas.
from django.db.models.signals import post_save, pre_delete
# Sinais disparados em salvamento/deleção.
from django.dispatch import receiver
# Decorador de registro de handlers.

from apps.academic.models import Guardian, Student
# Modelos acadêmicos com vínculos a perfis.

from .models import (
    Teacher,
    UserProfile,
    Enrollment,
    Invoice,
    PaymentPlan,
)
# Modelos escolares usados nas rotinas de sinal.


def _upsert_profile_for_user(
    user,
    *,
    role,
    tenant_id="",
    school=None,
    province="",
    district="",
):
    """Cria ou atualiza UserProfile com dados fornecidos, reativando se necessário."""
    if user is None:
        return

    profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            "role": role,
            "tenant_id": tenant_id or "",
            "school": school,
            "province": province or "",
            "district": district or "",
            "active": True,
        },
    )

    updates = []
    if profile.role != role:
        profile.role = role
        updates.append("role")
    if school is not None and profile.school_id != getattr(school, "id", None):
        profile.school = school
        updates.append("school")
    if tenant_id and profile.tenant_id != tenant_id:
        profile.tenant_id = tenant_id
        updates.append("tenant_id")
    if province and profile.province != province:
        profile.province = province
        updates.append("province")
    if district and profile.district != district:
        profile.district = district
        updates.append("district")
    if not profile.active:
        profile.active = True
        updates.append("active")

    if updates:
        profile.save(update_fields=updates)


@receiver(post_save, sender=get_user_model())
def ensure_user_profile(sender, instance, created, **kwargs):
    """Ao criar usuário, garante perfil padrão de admin nacional ativo."""
    if not created:
        return

    UserProfile.objects.get_or_create(
        user=instance,
        defaults={
            "role": "national_admin",
            "tenant_id": "",
            "province": "",
            "district": "",
            "active": True,
        },
    )


@receiver(pre_delete, sender=get_user_model())
def hard_delete_user_dependents(sender, instance, **kwargs):
    """Remove dependentes soft-delete antes de deletar usuário para evitar FKs."""
    # Ensure soft-deletable dependents are removed before the user to avoid FK violations.
    Teacher.all_objects.filter(user=instance).hard_delete()
    UserProfile.all_objects.filter(user=instance).hard_delete()
    # Clean up legacy tables that still reference auth_user but are no longer managed by models.
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='escola_professor';"
        )
        if cursor.fetchone():
            cursor.execute(
                "DELETE FROM escola_professor WHERE user_id = %s;",
                [instance.pk],
            )


@receiver(post_save, sender=Teacher)
def sync_teacher_profile(sender, instance, **kwargs):
    """Mantém UserProfile sincronizado quando um Teacher é salvo."""
    school = instance.school
    _upsert_profile_for_user(
        instance.user,
        role="teacher",
        tenant_id=instance.tenant_id or "",
        school=school,
        province=getattr(school, "province", "") if school else "",
        district=getattr(school, "district", "") if school else "",
    )


@receiver(post_save, sender=Student)
def sync_student_profile(sender, instance, **kwargs):
    """Garante perfil de aluno para o usuário do Student."""
    _upsert_profile_for_user(
        instance.user,
        role="student",
        tenant_id=instance.tenant_id or "",
    )


@receiver(post_save, sender=Guardian)
def sync_guardian_profile(sender, instance, **kwargs):
    """Garante perfil de encarregado para o usuário do Guardian."""
    _upsert_profile_for_user(
        instance.user,
        role="guardian",
        tenant_id=instance.tenant_id or "",
    )


def _month_range(start: date, end: date):
    """Gera datas do primeiro dia de cada mês entre start e end (inclusive)."""
    current = date(start.year, start.month, 1)
    while current <= end:
        yield current
        # next month
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)


@receiver(post_save, sender=Enrollment)
def create_finance_on_enrollment(sender, instance: Enrollment, created, **kwargs):
    """Cria fatura de matrícula e planos de pagamento ao matricular um aluno."""
    if not created:
        return

    tenant_id = instance.tenant_id
    student = instance.student
    classroom = instance.classroom
    school = classroom.school if classroom else None
    academic_year = classroom.academic_year if classroom else None

    # 1) Fatura de matrícula em rascunho
    if instance.enrollment_fee and instance.enrollment_fee > 0:
        inv = Invoice.objects.create(
            tenant_id=tenant_id,
            student=student,
            school=school,
            reference=f"MAT-{instance.code}",
            description=f"Taxa de matrícula {student.name}",
            amount=instance.enrollment_fee,
            due_date=instance.enrollment_date,
            status="draft",
        )
        PaymentPlan.objects.create(
            tenant_id=tenant_id,
            enrollment=instance,
            student=student,
            school=school,
            invoice=inv,
            type="enrollment_fee",
            description="Taxa de matrícula",
            amount=instance.enrollment_fee,
            due_date=instance.enrollment_date,
            status="invoiced",
        )

    # 2) Mensalidades até fim do ano letivo
    if instance.monthly_fee and instance.monthly_fee > 0 and academic_year:
        start_date = instance.monthly_fee_start or instance.enrollment_date
        end_date = instance.monthly_fee_end or academic_year.end_date
        for first_of_month in _month_range(start_date, end_date):
            due = date(first_of_month.year, first_of_month.month, min(first_of_month.day, academic_year.start_date.day))
            PaymentPlan.objects.create(
                tenant_id=tenant_id,
                enrollment=instance,
                student=student,
                school=school,
                type="tuition_monthly",
                description=f"Mensalidade {first_of_month.strftime('%m/%Y')}",
                amount=instance.monthly_fee,
                due_date=due,
                status="scheduled",
            )

    # 3) Propina (usa mensalidade como valor base, se existir)
    propina_val = instance.monthly_fee if instance.monthly_fee and instance.monthly_fee > 0 else Decimal("0")
    if propina_val > 0 and academic_year:
        PaymentPlan.objects.create(
            tenant_id=tenant_id,
            enrollment=instance,
            student=student,
            school=school,
            type="propina",
            description="Propina anual",
            amount=propina_val,
            due_date=academic_year.start_date,
            status="scheduled",
        )

    # 4) Taxas de exame NÃO são geradas no ato da matrícula; serão criadas apenas ao agendar o exame.
