from datetime import timedelta
from itertools import chain

from django.db.models import CharField, Value
from django.db.models import Prefetch
from django.utils import timezone

from main.helpers.weekdays import weekdays
from .ads import *
from .bookings import *
from .customer import *
from .driver import *
from .vehicles import *


class Dashboard(StaffUserRequiredMixin, TemplateView):
    template_name = 'admin_panel/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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

        return {
            **context,
            "users": users,
            "drivers_count": Driver.objects.filter(is_verified=True).count(),
            "customers_count": Customer.objects.filter(is_verified=True).count(),
            "ads_count": CustomerAd.objects.count() + DriverAd.objects.count(),
            "bookings_count": Booking.objects.exclude(status=Booking.PENDING).count(),
            "new_users_this_week": [
                User.objects.filter(date_joined__date=timezone.now().date() - timedelta(days=6)).count(),
                User.objects.filter(date_joined__date=timezone.now().date() - timedelta(days=5)).count(),
                User.objects.filter(date_joined__date=timezone.now().date() - timedelta(days=4)).count(),
                User.objects.filter(date_joined__date=timezone.now().date() - timedelta(days=3)).count(),
                User.objects.filter(date_joined__date=timezone.now().date() - timedelta(days=2)).count(),
                User.objects.filter(date_joined__date=timezone.now().date() - timedelta(days=1)).count(),
                User.objects.filter(date_joined__date=timezone.now().date()).count(),
            ],
            "weekdays": weekdays()
        }
