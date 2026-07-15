import logging

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from apps.authentication.models import VerificationToken

logger = logging.getLogger("audit")


class Command(BaseCommand):
    help = "Delete expired and used verification tokens."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted without actually deleting.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        now = timezone.now()

        tokens_to_delete = VerificationToken.objects.filter(
            Q(expires_at__lt=now) | Q(is_used=True)
        )
        count = tokens_to_delete.count()

        if dry_run:
            self.stdout.write(f"Dry run: would delete {count} tokens")
            return

        tokens_to_delete.delete()

        logger.info("token_cleanup deleted=%d", count)

        self.stdout.write(self.style.SUCCESS(f"Deleted {count} tokens"))
