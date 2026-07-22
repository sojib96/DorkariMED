"""
DRF throttle classes for authentication and OTP endpoints.

Uses ``AnonRateThrottle`` subclasses so that unauthenticated requests
are rate-limited by IP. Authenticated users are not throttled by these
classes (they are gated by separate per-user or per-IP policies if needed).
"""

from rest_framework.throttling import AnonRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    """
    Throttle login attempts per IP.

    Rate is configured via ``DEFAULT_THROTTLE_RATES["login"]`` in settings
    (default: 10/min, within the approved 3–15 range).
    """

    scope = "login"


class RegistrationRateThrottle(AnonRateThrottle):
    """
    Throttle registration attempts per IP.

    Rate is configured via ``DEFAULT_THROTTLE_RATES["registration"]`` in settings
    (default: 5/min, within the approved 3–15 range).
    """

    scope = "registration"


class OtpRateThrottle(AnonRateThrottle):
    """
    Throttle OTP send/verify attempts per IP.

    This is a shared throttle scope used by both the send and verify
    endpoints. Phone-based rate limiting is implemented in the view
    layer (cache-based counter); this IP-level throttle is a secondary
    abuse-prevention layer.

    Rate is configured via ``DEFAULT_THROTTLE_RATES["otp"]`` in settings
    (default: 5/min).
    """

    scope = "otp"
