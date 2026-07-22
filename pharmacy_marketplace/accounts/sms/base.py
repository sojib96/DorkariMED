"""
Abstract SMS sender interface.

Implementations must provide a ``send_sms`` method. In Phase 1, only
``ConsoleSmsSender`` is used (logs OTPs to console). A real SMS gateway
(e.g., Twilio, GreenWeb, SilkRoute) can be swapped in later by providing
a new implementation and updating the ``SMS_SENDER`` setting.
"""

from abc import ABC, abstractmethod


class SmsSender(ABC):
    """Abstract interface for sending SMS messages."""

    @abstractmethod
    def send_sms(self, phone: str, message: str) -> bool:
        """
        Send an SMS message to the given phone number.

        Args:
            phone: Recipient phone number (Bangladeshi format, e.g. 01712345678).
            message: Plain-text SMS body.

        Returns:
            ``True`` if the message was accepted for delivery, ``False`` otherwise.
        """
        ...
