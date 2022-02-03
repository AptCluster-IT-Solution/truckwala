import os

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import F
from django.utils import timezone
from num2words import num2words
from rest_framework.exceptions import ValidationError

from notifications.models import Notification
from users.models import Customer, Driver
from vehicles.models import Vehicle, VehicleCategory


class Ad(models.Model):
    description = models.CharField(max_length=255, default="")

    start_place = models.CharField(max_length=255)
    end_place = models.CharField(max_length=255)

    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)

    cost = models.PositiveIntegerField(default=0)

    product_type = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=255, null=True, blank=True)

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
    vehicle_category = models.ForeignKey(
        VehicleCategory,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="customer_ads",
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
    is_accepted = models.BooleanField(blank=True, null=True, default=True)

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        _is_adding = self._state.adding
        if _is_adding and self.ad.bids.filter(is_accepted=True).exists():
            raise ValidationError({"msg": "this ad is already accepted."})
        if not self.cost:
            self.cost = self.ad.cost
        super().save(force_insert, force_update, *args, **kwargs)

        if _is_adding and self.is_accepted:
            CustomerAd.objects.filter(id=self.ad.id).update(acceptor=self.bidder)
            Booking.objects.filter(customer_ad=self.ad).update(customer_bid_id=self.id, status=Booking.ACCEPTED)
            Notification.objects.create(
                notification_type=Notification.BID,
                subject=f"Order Accepted.",
                message=f"Your order from '{self.ad.start_place}' to '{self.ad.end_place}' has been confirmed. {self.ad.poster.user.full_name}  ({self.ad.poster.user.phone_number}) will contact you immediately.",
                entered_by=self.bidder.user,
                created_for=self.ad.poster.user,
                content_type=ContentType.objects.get_for_model(self),
                object_id=self.pk,
            )
            # Notification.objects.create(
            #     notification_type=Notification.BID,
            #     subject=f"You have accepted {self.bidder.user.full_name}'s ({self.bidder.user.phone_number})' request.",
            #     message=f"You have accepted {self.bidder.user.full_name}'s ({self.bidder.user.phone_number})' request.",
            #     entered_by=self.ad.poster.user,
            #     created_for=self.bidder.user,
            #     content_type=ContentType.objects.get_for_model(self),
            #     object_id=self.pk,
            # )


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
    is_accepted = models.BooleanField(blank=True, null=True, default=True)

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        _is_adding = self._state.adding
        if _is_adding and self.ad.bids.filter(is_accepted=True).exists():
            raise ValidationError({"msg": "this ad is already accepted."})
        super().save(force_insert, force_update, *args, **kwargs)

        if _is_adding and self.is_accepted:
            DriverAd.objects.filter(id=self.ad.id).update(acceptor=self.bidder)
            Booking.objects.filter(driver_ad=self.ad).update(driver_bid_id=self.id, status=Booking.ACCEPTED)

            Notification.objects.create(
                notification_type=Notification.BID,
                subject=f"Order Accepted",
                message=f"Your order has been confirmed, please contact {self.ad.poster.user.full_name}  ({self.ad.poster.user.phone_number}) for further process.",
                entered_by=self.bidder.user,
                created_for=self.ad.poster.user,
                content_type=ContentType.objects.get_for_model(self),
                object_id=self.pk,
            )
            # Notification.objects.create(
            #     notification_type=Notification.BID,
            #     subject=f"You have accepted {self.bidder.user.full_name}'s ({self.bidder.user.phone_number})' request.",
            #     message=f"You have accepted {self.bidder.user.full_name}'s ({self.bidder.user.phone_number})' request.",
            #     entered_by=self.ad.poster.user,
            #     created_for=self.bidder.user,
            #     content_type=ContentType.objects.get_for_model(self),
            #     object_id=self.pk,
            # )


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
        if self.driver_ad:
            return self.driver_ad.poster
        elif self.customer_bid:
            return self.customer_bid.bidder
        return None

    @property
    def customer(self):
        if self.customer_ad:
            return self.customer_ad.poster
        elif self.driver_bid:
            return self.driver_bid.bidder
        return None

    @property
    def cost(self):
        return self.bid.cost if hasattr(self.bid, "cost") else self.ad.cost

    @property
    def vehicle(self):
        return self.customer_bid.vehicle if self.customer_bid else self.ad.vehicle

    @property
    def commission(self):
        return self.vehicle.category.commission * self.cost

    @property
    def tax(self):
        return self.cost * 0.13

    @property
    def cost_with_tax(self):
        return self.cost + self.tax

    @property
    def cost_with_tax_in_words(self):
        return num2words(self.cost_with_tax).title()

    def __str__(self):
        return f"{str(self.ad)} - {str(self.created)}"

    def save(self, **kwargs):
        _is_adding = self._state.adding
        _just_completed = False

        try:
            if Booking.objects.get(pk=self.pk).status == Booking.FULFILLED:
                self.status = Booking.FULFILLED
        except Booking.DoesNotExist:
            pass

        if self.status == Booking.FULFILLED:
            try:
                if Booking.objects.get(pk=self.pk).status != Booking.FULFILLED:
                    _just_completed = True
            except Booking.DoesNotExist:
                pass
        super().save(**kwargs)
        if _is_adding:
            Transaction.objects.get_or_create(
                booking_id=self.pk,
                defaults={
                    "driver": self.driver,
                    "amount": self.cost,
                    "is_completed": False,
                }
            )
        if _just_completed:
            Transaction.objects.update_or_create(
                booking_id=self.pk,
                defaults={
                    "driver": self.driver,
                    "amount": self.cost,
                    "is_completed": True,
                }
            )
            Transaction.objects.filter(
                booking_id=None,
                driver_id=self.driver.pk,
                is_completed=False,
            ).update(
                amount=F('amount') + (self.vehicle.category.commission * self.cost)
            )
            Notification.objects.create(
                notification_type=Notification.BOOKING,
                subject=f"Order Completed",
                message=f"{self.ad.poster.user.full_name}  ({self.ad.poster.user.phone_number}) has delivered goods in drop off location. Please provide ratings and feedback.",
                created_for=self.customer.user,
                content_type=ContentType.objects.get_for_model(self),
                object_id=self.pk,
            )


class Transaction(models.Model):
    booking = models.OneToOneField(Booking, related_name='transactions', on_delete=models.CASCADE, blank=True,
                                   null=True)
    driver = models.ForeignKey(Driver, related_name='transactions', on_delete=models.CASCADE, null=True, blank=True)
    amount = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(default=timezone.now)
    is_completed = models.BooleanField(default=False, blank=True)

    def save(self, *args, **kwargs):
        self.date = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-date']
