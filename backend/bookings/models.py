from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from users.models import Customer, Driver
from vehicles.models import Vehicle


class Ad(models.Model):
    description = models.CharField(max_length=255, default="")

    start_place = models.CharField(max_length=255)
    end_place = models.CharField(max_length=255)

    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)

    cost = models.PositiveIntegerField(default=0)
    quantity = models.PositiveIntegerField(default=0)

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class CustomerAd(Ad):
    poster = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="posted_ads",
        blank=True
    )
    acceptor = models.ForeignKey(
        Driver,
        on_delete=models.CASCADE,
        related_name="accepted_ads",
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{str(self.poster)} - {str(self.created)}"


class CustomerAdBid(models.Model):
    ad = models.ForeignKey(CustomerAd, related_name='bids', on_delete=models.CASCADE)
    bidder = models.ForeignKey(
        Driver,
        on_delete=models.CASCADE,
        related_name="bid_ads",
        blank=True,
    )
    cost = models.PositiveIntegerField(default=0)
    description = models.TextField(max_length=1000, default="")
    is_accepted = models.BooleanField(blank=True, null=True)


class DriverAd(Ad):
    poster = models.ForeignKey(
        Driver,
        on_delete=models.CASCADE,
        related_name="posted_ads"
    )
    acceptor = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="accepted_ads",
        blank=True,
        null=True,
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="ads",
        null=True,
    )

    def __str__(self):
        return f"{str(self.poster)} - {str(self.created)}"


class DriverAdBid(models.Model):
    ad = models.ForeignKey(DriverAd, related_name='bids', on_delete=models.CASCADE)
    bidder = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="bid_ads",
        blank=True,
    )
    load = models.PositiveIntegerField(default=0)
    description = models.TextField(max_length=1000, default="")
    is_accepted = models.BooleanField(blank=True, null=True)


class Booking(models.Model):
    customer_ad = models.OneToOneField(
        CustomerAd, on_delete=models.CASCADE, blank=True, null=True
    )
    driver_ad = models.OneToOneField(
        DriverAd, on_delete=models.CASCADE, blank=True, null=True
    )

    PENDING = "P"
    ACCEPTED = "A"
    DISPATCHED = "D"
    FULFILLED = "F"
    STATUS_TYPES = (
        (PENDING, "Pending"),
        (ACCEPTED, "Accepted"),
        (DISPATCHED, "Dispatched"),
        (FULFILLED, "Fulfilled"),
    )
    status = models.CharField(max_length=1, choices=STATUS_TYPES, default=PENDING)
    created = models.DateTimeField(auto_now_add=True)

    @property
    def ad(self):
        return self.customer_ad if self.customer_ad else self.driver_ad

    def __str__(self):
        return f"{str(self.ad)} - {str(self.created)}"


class Transaction(models.Model):
    booking = models.ForeignKey(Booking, related_name='transactions', on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()