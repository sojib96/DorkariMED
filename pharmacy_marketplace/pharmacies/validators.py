"""
Validators for Pharmacy model fields.

Operating hours JSON validation:
- Keys must be valid day names (mon, tue, wed, thu, fri, sat, sun)
- Each day value must have ``open`` and ``close`` keys with valid ``HH:MM`` times
- ``open`` must be strictly before ``close``
- Days can be omitted (treated as closed) — validation only checks present days
"""

import re
from datetime import datetime

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

VALID_DAYS = {"mon", "tue", "wed", "thu", "fri", "sat", "sun"}
TIME_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


def validate_operating_hours(value):
    """
    Validate the ``operating_hours`` JSON structure for a Pharmacy.

    Called from the serializer layer (JSONField itself is schemaless).
    Accepts ``None`` (no hours set — valid).
    """
    if value is None:
        return

    if not isinstance(value, dict):
        raise ValidationError(
            _("Operating hours must be a JSON object with day keys."),
            code="invalid_type",
        )

    for day_key, schedule in value.items():
        # Validate day key
        if day_key not in VALID_DAYS:
            raise ValidationError(
                _("'%(day)s' is not a valid day key. Use: %(days)s"),
                params={"day": day_key, "days": ", ".join(sorted(VALID_DAYS))},
                code="invalid_day_key",
            )

        # Skip null/None (day is closed)
        if schedule is None:
            continue

        # Schedule must be a dict with open/close
        if not isinstance(schedule, dict):
            raise ValidationError(
                _("Schedule for '%(day)s' must be an object with 'open' and 'close' keys."),
                params={"day": day_key},
                code="invalid_schedule_type",
            )

        open_time = schedule.get("open")
        close_time = schedule.get("close")

        if not open_time or not close_time:
            raise ValidationError(
                _("Both 'open' and 'close' are required for '%(day)s'."),
                params={"day": day_key},
                code="missing_time",
            )

        # Validate time format
        for label, time_str in [("open", open_time), ("close", close_time)]:
            if not isinstance(time_str, str) or not TIME_RE.match(time_str):
                raise ValidationError(
                    _("'%(label)s' time for '%(day)s' must be in HH:MM format (got '%(value)s')."),
                    params={"label": label, "day": day_key, "value": time_str},
                    code="invalid_time_format",
                )

        # Validate open before close
        open_dt = datetime.strptime(open_time, "%H:%M")
        close_dt = datetime.strptime(close_time, "%H:%M")

        if open_dt >= close_dt:
            raise ValidationError(
                _("'open' time (%(open)s) must be before 'close' time (%(close)s) for '%(day)s'."),
                params={"open": open_time, "close": close_time, "day": day_key},
                code="open_after_close",
            )
