from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import post_save

from bookings.models import CustomerAd, DriverAd, Booking


@receiver(post_save, sender=CustomerAd)
def booking_create_on_ad_accept(**kwargs):
    ad = kwargs.get("instance")
    created = kwargs.get("created")

    if created:
        Booking.objects.create(customer_ad=ad)


@receiver(post_save, sender=DriverAd)
def booking_create_on_ad_accept(**kwargs):
    ad = kwargs.get("instance")
    created = kwargs.get("created")

    if created:
        Booking.objects.create(driver_ad=ad)
