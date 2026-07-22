"""
Management command to seed the initial superuser admin account.

Usage::

    python manage.py seed_admin [--phone 01700000000] [--password admin123]

If no arguments are provided, defaults from environment variables
``ADMIN_PHONE`` and ``ADMIN_PASSWORD`` are used, falling back to
hardcoded dev defaults (which must be changed before production).
"""

from django.conf import settings
from django.core.management.base import BaseCommand

from accounts.models import User


class Command(BaseCommand):
    help = "Seed the initial admin superuser account."

    def add_arguments(self, parser):
        parser.add_argument("--phone", type=str, default=None, help="Admin phone number")
        parser.add_argument("--password", type=str, default=None, help="Admin password")
        parser.add_argument(
            "--full-name",
            type=str,
            default="Platform Admin",
            help="Admin display name",
        )

    def handle(self, *args, **options):
        phone = options["phone"] or getattr(settings, "ADMIN_PHONE", "01700000000")
        password = options["password"] or getattr(settings, "ADMIN_PASSWORD", "admin123")
        full_name = options["full_name"]

        if User.objects.filter(phone=phone).exists():
            msg = f"Admin user with phone {phone} already exists. Skipping."
            self.stdout.write(self.style.WARNING(msg))
            return

        User.objects.create_superuser(
            phone=phone,
            password=password,
            full_name=full_name,
        )
        self.stdout.write(
            self.style.SUCCESS(f"Admin user created: phone={phone}, name={full_name}")
        )
