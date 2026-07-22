"""
DEV-ONLY SMS sender — logs OTP messages to console.

.. warning::

    This implementation is for **development and testing only**.
    It does NOT send real SMS messages. Replace with a real SMS gateway
    (e.g., Twilio, GreenWeb, SilkRoute) before deploying to production.

    Usage outside of ``DEBUG = True`` should be prevented by the
    ``warn_if_not_debug`` guard in this class or by a configuration
    check in ``settings/production.py``.
"""

import logging

from django.conf import settings

from accounts.sms.base import SmsSender

logger = logging.getLogger(__name__)


class ConsoleSmsSender(SmsSender):
    """
    Logs OTP messages to the console via Python logger.

    DEV-ONLY: Logs OTPs to console. Replace with real SMS gateway before production.
    """

    def __init__(self):
        if not settings.DEBUG:
            logger.warning(
                "ConsoleSmsSender is active outside DEBUG mode! "
                "This is a DEVELOPMENT-ONLY sender. No real SMS will be sent."
            )

    def send_sms(self, phone: str, message: str) -> bool:
        logger.info("=== SMS (DEV) === To: %s | Body: %s", phone, message)
        print(f"[SMS-DEV] To: {phone} | Message: {message}")
        return True
