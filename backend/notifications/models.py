from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from fcm_django.models import FCMDevice
from firebase_admin.messaging import Message, Notification as FirebaseNotification

User = get_user_model()


class Notification(models.Model):
    CUSTOMER_AD = "C"
    DRIVER_AD = "D"
    BID = "B"
    AD_ACCEPTED = "A"
    GLOBAL = "G"
    NOTIFICATION_TYPES = (
        (CUSTOMER_AD, "New Customer Ad"),
        (DRIVER_AD, "New Driver Ad"),
        (AD_ACCEPTED, "Ad Accepted"),
        (BID, "Bid Added"),
        (GLOBAL, "Global System-wide "),
    )
    notification_type = models.CharField(max_length=1, choices=NOTIFICATION_TYPES)

    subject = models.CharField(max_length=255)
    message = models.TextField()

    entered_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_notifications",
        null=True,
        blank=True,
    )
    created_for = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_notifications",
        null=True,
        blank=True,
    )

    seen = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, blank=True, null=True
    )
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        return self.subject

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert=False, force_update=False, using=None, update_fields=None)

        if self.created_for:
            user_device = FCMDevice.objects.filter(user=self.created_for)

        if self.notification_type == Notification.CUSTOMER_AD:
            user_device = FCMDevice.objects.filter(
                user__driver_profile__isnull=False
            ).distinct()

        if self.notification_type == Notification.DRIVER_AD:
            user_device = FCMDevice.objects.filter(
                user__customer_profile__isnull=False
            ).distinct()

        user_device.send_message(Message(notification=FirebaseNotification(title=self.subject, body=self.message)))
