# =============================================================================
# Dockerfile — Django application image
# =============================================================================
FROM python:3.12-slim

# ── System dependencies ──────────────────────────────────────────────────
# GDAL is required by GeoDjango for PostGIS support.
RUN apt-get update && apt-get install -y --no-install-recommends \
    binutils \
    libproj-dev \
    gdal-bin \
    && rm -rf /var/lib/apt/lists/*

# ── Python environment ───────────────────────────────────────────────────
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=pharmacy_marketplace.settings.production

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ── Health check ─────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/')" || exit 1

EXPOSE 8000

# Default command for production (override via docker-compose.yml for dev)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "pharmacy_marketplace.wsgi:application"]
