from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from fcm_django.models import FCMDevice

from bookings.models import Booking, CustomerAd, DriverAd, CustomerAdBid, DriverAdBid
from notifications.models import Notification


@receiver(pre_delete, sender=Booking)
@receiver(pre_delete, sender=CustomerAd)
@receiver(pre_delete, sender=DriverAd)
def delete_notification_on_sender_delete(**kwargs):
    instance = kwargs.get("instance")
    instance_ct = ContentType.objects.get_for_model(instance)
    Notification.objects.filter(
        object_id=instance.pk, content_type=instance_ct.id
    ).delete()
