from django.db import models

from core.models import BaseModel


class NotifySubscription(BaseModel):
    """
    "Notify me when X medicine is available near me" subscription.

    Customers subscribe to be notified when a specific medicine becomes
    available at a pharmacy within a radius. Fulfilled via polling or
    webhook in a future module — in Module 1 the subscription is stored
    for future notification (no real-time push).
    """

    customer_phone = models.CharField(
        max_length=15,
        db_index=True,
        help_text="Phone number to send notification to",
    )
    master_medicine = models.ForeignKey(
        "catalog.MasterMedicine",
        on_delete=models.CASCADE,
        related_name="notify_subscriptions",
        help_text="The medicine the customer wants to be notified about",
    )
    latitude = models.FloatField(
        help_text="Customer's reference latitude for proximity check"
    )
    longitude = models.FloatField(
        help_text="Customer's reference longitude for proximity check"
    )
    radius_km = models.PositiveIntegerField(
        default=5,
        help_text="Search radius in kilometers",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Is this subscription active?",
    )

    class Meta:
        db_table = "notifications_notify_subscription"
        verbose_name = "Notify Subscription"
        verbose_name_plural = "Notify Subscriptions"
        indexes = [
            models.Index(fields=["customer_phone", "master_medicine"]),
        ]

    def __str__(self):
        return f"{self.customer_phone} → {self.master_medicine}"
