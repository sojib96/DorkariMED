"""ASGI config for pharmacy_marketplace project."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pharmacy_marketplace.settings.dev")
application = get_asgi_application()
