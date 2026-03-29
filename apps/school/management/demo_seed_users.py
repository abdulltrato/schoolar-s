from datetime import date

from django.contrib.auth import get_user_model

from apps.school.models import AcademicYear, Grade, School


def ensure_users():
    user_model = get_user_model()
    admin, _ = user_model.objects.get_or_create(
        username="admin",
        defaults={"is_staff": True, "is_superuser": True},
    )
    admin.set_password("secret")
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()

    professor_user, _ = user_model.objects.get_or_create(username="prof1")
    professor_user.set_password("secret")
    professor_user.save()
    return admin, professor_user


def ensure_school():
    school, _ = School.objects.get_or_create(
        code="ESC-CENTRAL",
        defaults={
            "name": "School Primaria Central",
            "district": "KaMpfumo",
            "province": "Maputo Cidade",
            "active": True,
        },
    )
    return school


def ensure_academic_year():
    academic_year, _ = AcademicYear.objects.get_or_create(
        code="2026-2027",
        defaults={
            "start_date": date(2026, 2, 1),
            "end_date": date(2026, 12, 15),
            "active": True,
        },
    )
    return academic_year


def ensure_grades():
    classe_2, _ = Grade.objects.get_or_create(number=2, defaults={"cycle": 1, "name": "2a Grade"})
    classe_5, _ = Grade.objects.get_or_create(number=5, defaults={"cycle": 2, "name": "5a Grade"})
    return classe_2, classe_5
