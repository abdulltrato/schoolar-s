from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.school.models import AuditEvent


class Command(BaseCommand):
    help = "Delete persisted audit events older than the configured retention window."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=180,
            help="Retention window in days. Events older than this will be deleted.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview how many audit events would be deleted without writing changes.",
        )

    def handle(self, *args, **options):
        days = options["days"]
        dry_run = options["dry_run"]
        cutoff = timezone.now() - timedelta(days=days)
        queryset = AuditEvent.objects.filter(created_at__lt=cutoff)
        count = queryset.count()

        if dry_run:
            self.stdout.write(f"[DRY RUN] {count} audit events older than {days} days would be deleted.")
            return

        deleted, _ = queryset.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {deleted} audit events older than {days} days."))
