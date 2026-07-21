"""
Core abstract base models shared across all apps.

Every app model should inherit from BaseModel to get consistent
created_at / updated_at timestamps and a common primary key pattern.
"""

from django.db import models


class BaseModel(models.Model):
    """Abstract base with auto-updating timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
