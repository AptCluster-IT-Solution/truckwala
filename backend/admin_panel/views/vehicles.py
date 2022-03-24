from django.db.models import Q
from django.urls import reverse
from django.utils.html import escape
from django.views.generic import FormView
from django.views.generic import TemplateView
from django_datatables_view.base_datatable_view import BaseDatatableView

from admin_panel.forms import VehicleCategoryModelForm
from main.custom.permissions import StaffUserRequiredMixin
from vehicles.models import Vehicle, VehicleCategory


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
    columns = ['id', 'driver', 'registration_number', 'area_of_loading_space', 'category']

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
                escape(item.area_of_loading_space),
                escape(item.category.title),
            ])
        return json_data
