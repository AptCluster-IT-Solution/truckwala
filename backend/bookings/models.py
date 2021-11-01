import os

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from rest_framework.exceptions import ValidationError

from notifications.models import Notification
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

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        _is_adding = self._state.adding
        super().save(force_insert, force_update, *args, **kwargs)
        if _is_adding:
            Notification.objects.create(
                notification_type=Notification.CUSTOMER_AD,
                subject=f"{self.poster.user.full_name} is looking for a transport",
                message=f"{self.poster.user.full_name} is looking for a transport",
                entered_by=self.poster.user,
                content_type=ContentType.objects.get_for_model(self),
                object_id=self.pk,
            )
            Booking.objects.create(customer_ad_id=self.id)


class CustomerAdBid(models.Model):
    ad = models.ForeignKey(CustomerAd, related_name='bids', on_delete=models.CASCADE)
    bidder = models.ForeignKey(
        Driver,
        on_delete=models.CASCADE,
        related_name="bid_ads",
        blank=True,
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="bid_ads",
        blank=True,
    )
    cost = models.PositiveIntegerField(default=0)
    description = models.TextField(max_length=1000, default="")
    is_accepted = models.BooleanField(blank=True, null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__is_accepted = self.is_accepted

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        _is_adding = self._state.adding
        super().save(force_insert, force_update, *args, **kwargs)
        if _is_adding is False:
            if self.__is_accepted is None:
                if self.__is_accepted != self.is_accepted and self.is_accepted:
                    Notification.objects.create(
                        notification_type=Notification.BID,
                        subject=f"{self.ad.poster.user.full_name} has accepted your request.",
                        message=f"{self.ad.poster.user.full_name} has accepted your request.",
                        entered_by=self.ad.poster.user,
                        created_for=self.bidder.user,
                        content_type=ContentType.objects.get_for_model(self),
                        object_id=self.pk,
                    )
            else:
                raise ValidationError(
                    {"bid": f"This request is already {'accepted' if self.is_accepted else 'rejected'}"})
        else:
            Notification.objects.create(
                notification_type=Notification.BID,
                subject=f"{self.bidder.user.full_name} has requested to accept your ad.",
                message=f"{self.bidder.user.full_name} has requested to accept your ad.",
                entered_by=self.bidder.user,
                created_for=self.ad.poster.user,
                content_type=ContentType.objects.get_for_model(self),
                object_id=self.pk,
            )

        self.__is_accepted = self.is_accepted


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

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        _is_adding = self._state.adding
        super().save(force_insert, force_update, *args, **kwargs)
        if _is_adding:
            Notification.objects.create(
                notification_type=Notification.DRIVER_AD,
                subject=f"{self.poster.user.full_name} is looking for cargo to transport",
                message=f"{self.poster.user.full_name} is looking for cargo to transport",
                entered_by=self.poster.user,
                content_type=ContentType.objects.get_for_model(self),
                object_id=self.pk,
            )

            Booking.objects.create(driver_ad_id=self.id)


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__is_accepted = self.is_accepted

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        _is_adding = self._state.adding
        super().save(force_insert, force_update, *args, **kwargs)
        if _is_adding is False:
            if self.__is_accepted is None:
                if self.__is_accepted != self.is_accepted and self.is_accepted:
                    Notification.objects.create(
                        notification_type=Notification.BID,
                        subject=f"{self.ad.poster.user.full_name} has accepted your request.",
                        message=f"{self.ad.poster.user.full_name} has accepted your request.",
                        entered_by=self.ad.poster.user,
                        created_for=self.bidder.user,
                        content_type=ContentType.objects.get_for_model(self),
                        object_id=self.pk,
                    )
            else:
                raise ValidationError(
                    {"bid": f"This request is already {'accepted' if self.is_accepted else 'rejected'}"})
        else:
            Notification.objects.create(
                notification_type=Notification.BID,
                subject=f"{self.bidder.user.full_name} has requested to accept your ad.",
                message=f"{self.bidder.user.full_name} has requested to accept your ad.",
                entered_by=self.bidder.user,
                created_for=self.ad.poster.user,
                content_type=ContentType.objects.get_for_model(self),
                object_id=self.pk,
            )
        self.__is_accepted = self.is_accepted


def get_invoice_image_path(_, filename):
    return os.path.join("images/invoices/", filename)


class Booking(models.Model):
    customer_ad = models.OneToOneField(
        CustomerAd, on_delete=models.CASCADE, blank=True, null=True
    )
    customer_bid = models.OneToOneField(
        CustomerAdBid, on_delete=models.CASCADE, blank=True, null=True
    )

    driver_ad = models.OneToOneField(
        DriverAd, on_delete=models.CASCADE, blank=True, null=True
    )
    driver_bid = models.OneToOneField(
        DriverAdBid, on_delete=models.CASCADE, blank=True, null=True
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
    invoice_image = models.ImageField(upload_to=get_invoice_image_path, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    @property
    def ad(self):
        return self.customer_ad if self.customer_ad else self.driver_ad

    @property
    def bid(self):
        return self.customer_bid if self.customer_bid else self.driver_bid

    @property
    def driver(self):
        return self.customer_bid.bidder if self.customer_bid else self.driver_bid.ad.acceptor

    @property
    def customer(self):
        return self.customer_ad.poster if self.customer_ad else self.driver_ad.poster

    @property
    def cost(self):
        return self.bid.cost if hasattr(self.bid, "cost") else self.ad.cost

    @property
    def vehicle(self):
        return self.customer_bid.vehicle if self.customer_bid else self.ad.vehicle

    @property
    def commission(self):
        return self.vehicle.category.commission * self.cost

    def __str__(self):
        return f"{str(self.ad)} - {str(self.created)}"

    def save(self, **kwargs):
        just_completed = False
        if self.status == self.FULFILLED:
            try:
                if Booking.objects.get(pk=self.pk).status != self.FULFILLED:
                    just_completed = True
            except Booking.DoesNotExist:
                pass
        super().save(**kwargs)
        if just_completed:
            Transaction.objects.update_or_create(
                booking_id=self.pk,
                driver_id=self.driver.pk,
                defaults={
                    "amount": self.cost
                }
            )


class Transaction(models.Model):
    booking = models.OneToOneField(Booking, related_name='transactions', on_delete=models.CASCADE, blank=True,
                                   null=True)
    driver = models.ForeignKey(Driver, related_name='transactions', on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
