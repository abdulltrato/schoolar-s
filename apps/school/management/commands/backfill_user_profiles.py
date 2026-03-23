from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import connection

from apps.academic.models import Guardian, Student
from apps.school.models import Teacher, UserProfile


class Command(BaseCommand):
    help = "Create missing user profiles from existing teacher, student, and guardian relations."

    def add_arguments(self, parser):
        parser.add_argument(
            "--default-role",
            default="national_admin",
            help="Fallback role for users without a linked domain record.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview the profiles that would be created without writing changes.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        default_role = options["default_role"]
        created = 0
        skipped = 0

        if UserProfile._meta.db_table not in connection.introspection.table_names():
            self.stdout.write(
                self.style.WARNING(
                    "UserProfile table is not available yet. Sync the database schema before running this command."
                )
            )
            return

        user_model = get_user_model()
        users = user_model.objects.all().select_related("school_profile")

        for user in users:
            if hasattr(user, "school_profile"):
                skipped += 1
                continue

            profile_data = self._infer_profile_data(user, default_role)
            if dry_run:
                self.stdout.write(
                    f"[DRY RUN] {user.username}: role={profile_data['role']} tenant={profile_data['tenant_id'] or '-'}"
                )
                created += 1
                continue

            UserProfile.objects.create(user=user, **profile_data)
            created += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f"Created profile for {user.username} with role={profile_data['role']}"
                )
            )

        self.stdout.write(
            f"Backfill finished. created={created} skipped_existing={skipped} dry_run={dry_run}"
        )

    def _infer_profile_data(self, user, default_role):
        teacher = Teacher.objects.filter(user=user).select_related("school").first()
        if teacher:
            return {
                "role": "teacher",
                "school": teacher.school,
                "tenant_id": teacher.tenant_id or "",
                "province": getattr(teacher.school, "province", "") if teacher.school else "",
                "district": getattr(teacher.school, "district", "") if teacher.school else "",
                "active": True,
            }

        student = Student.objects.filter(user=user).first()
        if student:
            return {
                "role": "student",
                "school": None,
                "tenant_id": student.tenant_id or "",
                "province": "",
                "district": "",
                "active": True,
            }

        guardian = Guardian.objects.filter(user=user).first()
        if guardian:
            return {
                "role": "guardian",
                "school": None,
                "tenant_id": guardian.tenant_id or "",
                "province": "",
                "district": "",
                "active": True,
            }

        return {
            "role": default_role,
            "school": None,
            "tenant_id": "",
            "province": "",
            "district": "",
            "active": True,
        }
