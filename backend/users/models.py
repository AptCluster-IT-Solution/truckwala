import os

from django.apps import apps
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models, transaction
from django.db.models import Sum, F, Value, Q
from django.db.models.functions import Coalesce


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email, and password.
        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, db_index=True, blank=True, null=True)
    GENDER_CHOICES = [("M", "Male"), ("F", "Female"), ("D", "Do not specify")]
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, null=True, blank=True
    )
    full_name = models.CharField(max_length=100, null=True, blank=True)

    phone_number = models.CharField(unique=True, max_length=20, db_index=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, default="kathmandu")
    pan_number = models.CharField(blank=True, null=True, max_length=255)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return str(self.full_name)

    class Meta:
        verbose_name = "User"

    @transaction.atomic
    def save(self, *args, **kwargs):
        if not self.full_name:
            self.first_name = self.first_name.capitalize()
            self.last_name = self.last_name.capitalize()
            self.full_name = f"{self.first_name} {self.last_name}"
        else:
            self.full_name = self.full_name.capitalize()

        super(User, self).save(*args, **kwargs)


class Driver(models.Model):
    user: User = models.OneToOneField(
        User, related_name="driver_profile", on_delete=models.CASCADE
    )
    is_verified = models.BooleanField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        _is_adding = self._state.adding
        super().save(*args, **kwargs)
        if _is_adding:
            apps.get_model("bookings", "Transaction").objects.get_or_create(
                booking_id=None,
                driver_id=self.id,
                is_completed=False,
                defaults={
                    "amount": 0
                }
            )

    def __str__(self):
        return str(self.user.full_name)

    @property
    def paid_amount(self):
        return apps.get_model("bookings", "Transaction").objects.filter(
            driver_id=self.pk, booking__isnull=True, is_completed=True,
        ).aggregate(paid_amount=Coalesce(Sum('amount'), Value(0)))["paid_amount"]

    @property
    def earned_amount(self):
        return apps.get_model("bookings", "Transaction").objects.filter(
            driver_id=self.pk, booking__isnull=False, is_completed=True,
        ).aggregate(
            earned_amount=Coalesce(Sum('amount'), Value(0))
        )["earned_amount"] - self.paid_amount

    @property
    def due_amount(self):
        # ads by customer commission + ads by driver commission - total paid till now
        # return \
        #     apps.get_model("bookings", "Booking").objects.filter(
        #         customer_bid__bidder__id=self.id
        #     ).aggregate(
        #         commission=Coalesce(
        #             Sum(F('customer_bid__vehicle__category__commission') * F('customer_bid__cost') / 100),
        #             Value(0))
        #     )['commission'] + \
        #     apps.get_model("bookings", "Booking").objects.filter(
        #         driver_bid__ad__poster__id=self.id
        #     ).aggregate(
        #         commission=Coalesce(
        #             Sum(F('driver_bid__ad__vehicle__category__commission') * F('driver_bid__ad__cost') / 100),
        #             Value(0))
        #     )['commission'] - \
        #     self.paid_amount
        return apps.get_model("bookings", "Transaction").objects.get_or_create(
                booking_id=None,
                driver_id=self.id,
                is_completed=False,
                defaults={
                    "amount": 0
                }
            )[0].amount

    @property
    def bookings(self):
        return apps.get_model("bookings", "Booking").objects.filter(
            Q(customer_bid__bidder__id=self.id) | Q(driver_bid__ad__poster__id=self.id)
        ).order_by("-created")


class Customer(models.Model):
    user: User = models.OneToOneField(
        User, related_name="customer_profile", on_delete=models.CASCADE
    )
    is_verified = models.BooleanField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user.full_name)


def get_user_document_path(_, filename):
    return os.path.join("images/documents/", filename)


class DriverDocument(models.Model):
    driver: Driver = models.ForeignKey(
        Driver, on_delete=models.CASCADE, related_name="documents"
    )
    image = models.ImageField(upload_to=get_user_document_path)

    def __str__(self):
        return str(self.driver)


class CustomerDocument(models.Model):
    customer: Customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="documents"
    )
    image = models.ImageField(upload_to=get_user_document_path)

    def __str__(self):
        return str(self.customer)
