"""
Cursor-based pagination for DRF viewsets.

Uses the model's `created_at` or `id` field as the cursor. This is the
default pagination class for all API endpoints (set in base.py settings).

Why cursor-based:
- Stable under concurrent writes (unstable ordering risk with page numbers)
- Constant-time for deep paging
- No "page disappeared" or "offset explosion" issues
"""

from rest_framework.pagination import CursorPagination


class CursorPageNumberPagination(CursorPagination):
    """Default cursor pagination ordered by creation time (descending)."""

    ordering = "-created_at"
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
