from django.db import transaction
from django.db.models import Q
from django.shortcuts import redirect
from django.utils.html import escape
from django.views.generic import DetailView
from django.views.generic import TemplateView
from django_datatables_view.base_datatable_view import BaseDatatableView

from bookings.models import Transaction
from main.custom.permissions import StaffUserRequiredMixin
from users.models import Driver
from users.models import User


class DriverProfile(DetailView):
    model = Driver
    context_object_name = 'driver'
    template_name = 'admin_panel/htmx/driver_detail.html'


class DriversPage(StaffUserRequiredMixin, TemplateView):
    template_name = 'admin_panel/drivers.html'


def driver_delete(request, pk=None):
    User.objects.filter(driver_profile__pk=pk).delete()
    return redirect('drivers_page')


class UnverifiedDriversPage(StaffUserRequiredMixin, TemplateView):
    template_name = 'admin_panel/unverified_drivers.html'


def driver_payment(request):
    try:
        with transaction.atomic():
            driver_id = request.POST.get('driver_id')
            amount = request.POST.get('amount')
            Transaction.objects.create(driver_id=driver_id, amount=amount, is_completed=True)
    except Exception as _:
        pass
    return redirect('drivers_page')


class DriversListJson(StaffUserRequiredMixin, BaseDatatableView):
    model = Driver
    columns = ['id', 'user__full_name', 'user__phone_number', 'user__email', 'vehicles__registration_number',
               'vehicles__area_of_loading_space', 'due_amount', 'created', 'documents']

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
                item.vehicles.first().registration_number if item.vehicles.count() else None,
                item.vehicles.first().area_of_loading_space if item.vehicles.count() else None,
                item.due_amount,
                item.user.date_joined.strftime("%Y-%m-%d %H:%M:%S"),
                list(item.documents.all().values_list("image", flat=True))
            ])
        return json_data


class UnverifiedDriversListJson(DriversListJson):
    def get_initial_queryset(self):
        return Driver.objects.filter(is_verified__isnull=True)
