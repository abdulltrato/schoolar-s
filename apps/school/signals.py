from django.contrib.auth import get_user_model
from django.db import connection
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from apps.academic.models import Guardian, Student

from .models import Teacher, UserProfile


def _upsert_profile_for_user(
    user,
    *,
    role,
    tenant_id="",
    school=None,
    province="",
    district="",
):
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
    _upsert_profile_for_user(
        instance.user,
        role="student",
        tenant_id=instance.tenant_id or "",
    )


@receiver(post_save, sender=Guardian)
def sync_guardian_profile(sender, instance, **kwargs):
    _upsert_profile_for_user(
        instance.user,
        role="guardian",
        tenant_id=instance.tenant_id or "",
    )
