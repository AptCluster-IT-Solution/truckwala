from datetime import timedelta
from itertools import chain

from django.db.models import Q, F, Prefetch
from django.db.models import CharField, Value
from django.db.models.aggregates import Count
from django.db.models.functions import TruncDay, TruncDate
from django.utils import timezone

from bookings.models import CustomerAd, DriverAd, Booking
from users.models import User, Driver, Customer


def dashboard(request):
    if (
            request.path == "/"
            and request.user.is_authenticated
            and request.user.is_superuser
    ):
        driver_users = (
            User.objects.prefetch_related(Prefetch("driver_profile", to_attr="profile"))
                .filter(
                driver_profile__isnull=False, driver_profile__is_verified__isnull=True
            )
                .distinct()
                .annotate(user_type=Value("d", output_field=CharField()))
        )

        customer_users = (
            User.objects.prefetch_related(
                Prefetch("customer_profile", to_attr="profile")
            )
                .filter(
                customer_profile__isnull=False,
                customer_profile__is_verified__isnull=True,
            )
                .distinct()
                .annotate(user_type=Value("c", output_field=CharField()))
        )

        users = sorted(
            chain(driver_users, customer_users),
            key=lambda instance: instance.driver_profile.created
            if hasattr(instance, "driver_profile")
            else instance.customer_profile.created,
        )

        print(timezone.now().date() - timedelta(days=7))

        print(User.objects.filter(
            date_joined__gt=timezone.now().date() - timedelta(days=7),
        ).annotate(
            created_count=Count('date_joined__date')
        ).values_list('created_count', flat=True))

        return {
            "users": users,
            "drivers_count": Driver.objects.filter(is_verified=True).count(),
            "customers_count": Customer.objects.filter(is_verified=True).count(),
            "ads_count": CustomerAd.objects.count() + DriverAd.objects.count(),
            "bookings_count": Booking.objects.exclude(status=Booking.PENDING).count(),
            "new_users_this_week": list(User.objects.annotate(date=TruncDate('date_joined'
)).values('date').annotate(c=Count('id')).values_list(
'c', flat=True))
        }
    return {}
