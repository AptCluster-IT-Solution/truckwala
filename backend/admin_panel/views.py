from datetime import timedelta
from itertools import chain

from django.db import transaction
from django.db.models import CharField, Value, Q
from django.db.models import Prefetch
from django.db.models.aggregates import Count
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape
from django.views.generic import TemplateView, FormView
from django_datatables_view.base_datatable_view import BaseDatatableView

from admin_panel.forms import VehicleCategoryModelForm, TransactionModelForm
from bookings.models import CustomerAd, DriverAd, Booking, Transaction
from main.custom.permissions import StaffUserRequiredMixin
from main.helpers.weekdays import weekdays
from users.models import User, Driver, Customer
from vehicles.models import Vehicle, VehicleCategory


class Dashboard(StaffUserRequiredMixin, TemplateView):
    template_name = 'admin_panel/dashboard.html'

    def get_context_data(self, **kwargs):
        print(self.request.build_absolute_uri)
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


class DriversPage(StaffUserRequiredMixin, TemplateView):
    template_name = 'admin_panel/drivers.html'


class UnverifiedDriversPage(StaffUserRequiredMixin, TemplateView):
    template_name = 'admin_panel/unverified_drivers.html'


def driver_payment(request):
    try:
        with transaction.atomic():
            driver_id = request.POST.get('driver_id')
            amount = request.POST.get('amount')
            Transaction.objects.create(driver_id=driver_id, amount=amount)
    except Exception as _:
        pass
    return redirect('drivers_page')


class DriversListJson(StaffUserRequiredMixin, BaseDatatableView):
    model = Driver
    columns = ['id', 'user__full_name', 'user__phone_number', 'user__email', 'created', 'due_amount', 'documents']

    def get_initial_queryset(self):
        return Driver.objects.filter(is_verified=True)

    def filter_queryset(self, qs):
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(Q(user__full_name__istartswith=search) |
                           Q(user__phone_number__istartswith=search) |
                           Q(user__email__istartswith=search))
        return qs

    def prepare_results(self, qs):
        # prepare list with output column data
        # queryset is already paginated here
        json_data = []
        for item in qs:
            json_data.append([
                escape(item.id),  # escape HTML for security reasons
                # escape("{0} {1}".format(item.customer_firstname, item.customer_lastname)),
                # escape HTML for security reasons
                # item.get_state_display(),
                item.user.full_name,
                item.user.phone_number,
                item.user.email,
                item.user.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
                item.due_amount,
                list(item.documents.all().values_list("image", flat=True))
            ])
        return json_data


class UnverifiedDriversListJson(DriversListJson):
    def get_initial_queryset(self):
        return Driver.objects.filter(is_verified__isnull=True)


class CustomersPage(StaffUserRequiredMixin, TemplateView):
    template_name = 'admin_panel/customers.html'

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     return {
    #         **context,
    #         "users": User.objects.prefetch_related(
    #             Prefetch("customer_profile", to_attr="profile")
    #         )
    #             .filter(
    #             customer_profile__isnull=False,
    #             customer_profile__is_verified__isnull=True,
    #         )
    #             .distinct()
    #             .annotate(user_type=Value("c", output_field=CharField()))
    #     }


class CustomersListJson(StaffUserRequiredMixin, BaseDatatableView):
    model = Customer
    columns = ['id', 'user__full_name', 'user__phone_number', 'user__email', 'created']

    def filter_queryset(self, qs):
        # qs = qs.filter(is_verified=True)
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(Q(user__full_name__istartswith=search) |
                           Q(user__phone_number__istartswith=search) |
                           Q(user__email__istartswith=search))
        return qs

    def prepare_results(self, qs):
        json_data = []
        for item in qs:
            json_data.append([
                escape(item.id),
                escape(item.user.full_name),
                escape(item.user.phone_number),
                escape(item.user.email),
                escape(item.user.date_joined.strftime("%Y-%m-%d %H:%M:%S")),
            ])
        return json_data


class VehicleCategoriesPage(StaffUserRequiredMixin, FormView):
    template_name = 'admin_panel/vehicle_categories.html'
    form_class = VehicleCategoryModelForm

    def get_success_url(self):
        return reverse('vehicle_categories_page')

    def get_form(self, form_class=None):
        form_class = form_class if form_class else self.form_class
        try:
            instance = VehicleCategory.objects.get(pk=self.kwargs.get("pk"))
            return form_class(instance=instance, **self.get_form_kwargs())
        except VehicleCategory.DoesNotExist:
            return form_class(**self.get_form_kwargs())

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class VehicleCategoriesListJson(StaffUserRequiredMixin, BaseDatatableView):
    model = VehicleCategory
    columns = ['id', 'title', 'commission']

    def filter_queryset(self, qs):
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(Q(title__istartswith=search))
        return qs

    def prepare_results(self, qs):
        json_data = []
        for item in qs:
            json_data.append([
                escape(item.id),
                escape(item.title),
                escape(item.commission),
            ])
        return json_data


class VehiclesPage(StaffUserRequiredMixin, TemplateView):
    template_name = 'admin_panel/vehicles.html'


class VehiclesListJson(StaffUserRequiredMixin, BaseDatatableView):
    model = Vehicle
    columns = ['id', 'driver', 'registration_number', 'capacity', 'category']

    def filter_queryset(self, qs):
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(Q(driver__user__full_name__istartswith=search) | Q(registration_number__istartswith=search))
        return qs

    def prepare_results(self, qs):
        json_data = []
        for item in qs:
            json_data.append([
                escape(item.id),
                escape(item.driver.user.full_name),
                escape(item.registration_number),
                escape(item.capacity),
                escape(item.category.title),
            ])
        return json_data


class DriverAdsPage(StaffUserRequiredMixin, TemplateView):
    template_name = 'admin_panel/driver_ads.html'


class DriverAdsListJson(StaffUserRequiredMixin, BaseDatatableView):
    model = DriverAd
    columns = ['id', 'driver', 'customer', 'vehicle', 'start_place', 'end_place',
               'start_time', 'end_time', 'cost', 'quantity', 'created', ]

    def filter_queryset(self, qs):
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(poster__user__full_name__istartswith=search) |
                Q(vehicle__registration_number__istartswith=search) |
                Q(start_place__istartswith=search) |
                Q(end_place__istartswith=search)
            )
        return qs

    def prepare_results(self, qs):
        # prepare list with output column data
        # queryset is already paginated here
        json_data = []
        for item in qs:
            json_data.append([
                escape(item.id),
                escape(item.poster.user.full_name),
                escape(item.acceptor.user.full_name) if item.acceptor else None,
                escape(item.vehicle.registration_number) if item.vehicle else None,
                escape(item.start_place),
                escape(item.end_place),
                escape(item.start_time.strftime("%Y-%m-%d %H:%M") if item.start_time else None),
                escape(item.end_time.strftime("%Y-%m-%d %H:%M") if item.end_time else None),
                escape(item.cost),
                escape(item.quantity),
                escape(item.created.strftime("%Y-%m-%d %H:%M")),
            ])
        return json_data


class CustomerAdsPage(StaffUserRequiredMixin, TemplateView):
    template_name = 'admin_panel/customer_ads.html'


class CustomerAdsListJson(StaffUserRequiredMixin, BaseDatatableView):
    model = CustomerAd
    columns = ['id', 'customer', 'driver', 'start_place', 'end_place',
               'start_time', 'end_time', 'cost', 'quantity', 'created', ]

    def filter_queryset(self, qs):
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(poster__user__full_name__istartswith=search) |
                Q(start_place__istartswith=search) |
                Q(end_place__istartswith=search)
            )
        return qs

    def prepare_results(self, qs):
        json_data = []
        for item in qs:
            json_data.append([
                escape(item.id),
                escape(item.poster.user.full_name),
                escape(item.acceptor.user.full_name) if item.acceptor else None,
                escape(item.start_place),
                escape(item.end_place),
                escape(item.start_time.strftime("%Y-%m-%d %H:%M") if item.start_time else None),
                escape(item.end_time.strftime("%Y-%m-%d %H:%M") if item.end_time else None),
                escape(item.cost),
                escape(item.quantity),
                escape(item.created.strftime("%Y-%m-%d %H:%M")),
            ])
        return json_data


class BookingsPage(StaffUserRequiredMixin, TemplateView):
    template_name = 'admin_panel/bookings.html'


class BookingsListJson(StaffUserRequiredMixin, BaseDatatableView):
    model = Booking
    columns = ['id', 'driver', 'customer', 'vehicle', 'vehicle_category', 'start_place', 'end_place', 'price', 'status',
               'created', ]

    def filter_queryset(self, qs):
        qs = qs.filter(Q(status__in=[Booking.ACCEPTED, Booking.DISPATCHED, Booking.FULFILLED]))
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(customer_ad__poster__user__full_name__istartswith=search) |
                Q(driver_ad__poster__user__full_name__istartswith=search) |
                Q(customer_bid__bidder__user__full_name__istartswith=search) |
                Q(driver_bid__bidder__user__full_name__istartswith=search) |

                Q(customer_bid__vehicle__registration_number__istartswith=search) |
                Q(driver_ad__vehicle__registration_number__istartswith=search)
            )

        return qs

    def prepare_results(self, qs):
        json_data = []
        for item in qs:
            details = {
                'start_place': item.ad.start_place,
                'end_place': item.ad.end_place,
            }
            if item.customer_ad:
                details['driver'] = item.bid.bidder.user.full_name
                details['customer'] = item.ad.poster.user.full_name
                details['vehicle'] = item.bid.vehicle.registration_number
                details['vehicle_category'] = item.bid.vehicle.category.title
                details['price'] = item.bid.cost
            else:
                details['customer'] = item.bid.bidder.user.full_name
                details['driver'] = item.ad.poster.user.full_name
                details['vehicle'] = item.ad.vehicle.registration_number
                details['vehicle_category'] = item.ad.vehicle.category.title
                details['price'] = item.ad.cost

            json_data.append([
                escape(item.id),
                escape(details['driver']),
                escape(details['customer']),
                escape(details['vehicle']),
                escape(details['vehicle_category']),
                escape(details['start_place']),
                escape(details['end_place']),
                escape(details['price']),
                escape(dict(Booking.STATUS_TYPES).get(item.status)),
                escape(item.created.strftime("%Y-%m-%d %H:%M")),
            ])
        return json_data


class CustomerToDriverTransactionsPage(StaffUserRequiredMixin, TemplateView):
    template_name = 'admin_panel/customer_transactions.html'


class CustomerToDriverTransactionsListJson(StaffUserRequiredMixin, BaseDatatableView):
    model = Transaction
    columns = ['id', 'driver', 'customer', 'amount', 'is_completed', 'created']

    def get_initial_queryset(self):
        return Transaction.objects.filter(booking__isnull=False)

    def filter_queryset(self, qs):
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(
                Q(driver__user__full_name__istartswith=search) |
                Q(booking__customer_ad__poster__user__full_name__istartswith=search) |
                Q(booking__driver_bid__bidder__user__full_name__istartswith=search)
            )

        return qs

    def prepare_results(self, qs):
        json_data = []
        for item in qs:
            json_data.append([
                escape(item.id),
                escape(item.driver.user.full_name),
                escape(item.booking.customer.user.full_name) if item.booking else None,
                escape(item.amount),
                escape(item.is_completed),
                escape(item.date.strftime("%Y-%m-%d %H:%M")),
            ])
        return json_data


class DriverToAdminTransactionsPage(StaffUserRequiredMixin, TemplateView):
    template_name = 'admin_panel/driver_transactions.html'


class DriverToAdminTransactionsListJson(CustomerToDriverTransactionsListJson):
    columns = ['id', 'driver', 'amount', 'is_completed', 'created']

    def get_initial_queryset(self):
        return Transaction.objects.filter(booking__isnull=True)

    def prepare_results(self, qs):
        json_data = []
        for item in qs:
            json_data.append([
                escape(item.id),
                escape(item.driver.user.full_name),
                escape(item.amount),
                escape(item.is_completed),
                escape(item.date.strftime("%Y-%m-%d %H:%M")),
            ])
        return json_data
