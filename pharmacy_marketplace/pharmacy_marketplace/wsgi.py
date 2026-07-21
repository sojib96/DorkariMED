"""WSGI config for pharmacy_marketplace project."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pharmacy_marketplace.settings.dev")
application = get_wsgi_application()
