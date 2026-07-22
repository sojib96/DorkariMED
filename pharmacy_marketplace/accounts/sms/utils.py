"""
SMS sender resolution — returns the configured ``SmsSender`` instance.

In Phase 1 this always returns ``ConsoleSmsSender``. A future settings
entry (``SMS_SENDER_CLASS``) will allow swapping to a real gateway.
"""

from django.conf import settings


def get_sms_sender():
    """
    Return an ``SmsSender`` instance based on current configuration.

    Phase 1 always uses ``ConsoleSmsSender``. The import is deferred
    to avoid circular imports at module load time.
    """
    from accounts.sms.console import ConsoleSmsSender

    sender_class_path = getattr(settings, "SMS_SENDER_CLASS", None)

    if sender_class_path is not None:
        # Future: resolve dotted path and instantiate (e.g., "accounts.sms.twilio.TwilioSmsSender")
        import importlib
        module_path, class_name = sender_class_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        sender_class = getattr(module, class_name)
        return sender_class()

    return ConsoleSmsSender()
