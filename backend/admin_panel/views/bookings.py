from django.db.models import Q
from django.utils.html import escape
from django.views.generic import TemplateView
from django_datatables_view.base_datatable_view import BaseDatatableView

from bookings.models import Booking
from bookings.models import Transaction
from main.custom.permissions import StaffUserRequiredMixin


class BookingsPage(StaffUserRequiredMixin, TemplateView):
    template_name = 'admin_panel/bookings.html'


class BookingsListJson(StaffUserRequiredMixin, BaseDatatableView):
    model = Booking
    columns = ['id', 'driver', 'customer', 'initiator', 'vehicle', 'vehicle_category', 'start_place', 'end_place',
               'price', 'status', 'created', ]

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
                'initiator': item.started_by,
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
                escape(details['initiator']),
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
                escape(item.driver.user.full_name) if item.driver else None,
                escape(item.booking.customer.user.full_name) if item.booking and item.booking.customer else None,
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
