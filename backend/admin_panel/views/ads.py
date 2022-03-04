from django.db.models import Q
from django.utils.html import escape
from django.views.generic import TemplateView
from django_datatables_view.base_datatable_view import BaseDatatableView

from bookings.models import CustomerAd, DriverAd
from main.custom.permissions import StaffUserRequiredMixin


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
