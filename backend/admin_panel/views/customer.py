from django.db.models import Q
from django.shortcuts import redirect
from django.utils.html import escape
from django.views.generic import TemplateView
from django_datatables_view.base_datatable_view import BaseDatatableView

from main.custom.permissions import StaffUserRequiredMixin
from users.models import User, Customer


def customer_delete(request, pk=None):
    User.objects.filter(customer_profile__pk=pk).delete()
    return redirect('customers_page')


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
