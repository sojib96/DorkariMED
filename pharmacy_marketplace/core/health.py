"""
Health-check endpoint for Docker/load-balancer probing.

Returns 200 OK with JSON status if the application is running.
"""

from django.db import connection
from django.http import JsonResponse


def health_check(request):
    """Basic health check — returns JSON with database connectivity status."""
    db_status = "ok"
    db_error = None
    try:
        connection.ensure_connection()
    except Exception as e:
        db_status = "error"
        db_error = str(e)

    status_code = 200 if db_status == "ok" else 503
    return JsonResponse(
        {
            "status": "healthy" if db_status == "ok" else "degraded",
            "database": db_status,
            "db_error": db_error,
        },
        status=status_code,
    )
