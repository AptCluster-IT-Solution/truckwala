from rest_framework import viewsets
from rest_framework.response import Response

from main.custom.permissions import ActionBasedPermission, IsPosterOrReadOnly, IsDriver
from vehicles.models import Vehicle, VehicleCategory
from vehicles.serializers import VehicleSerializer, VehicleCategorySerializer


class VehicleModelViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleSerializer
    permission_classes = [ActionBasedPermission]
    action_permissions = {
        IsPosterOrReadOnly: ["update", "partial_update", "destroy", "list", "retrieve"],
        IsDriver: ["create"],
    }

    def get_queryset(self):
        if self.request.user.is_authenticated():
            return Vehicle.objects.filter(driver__user=self.request.user)
        return Vehicle.objects.none()

    def perform_create(self, serializer):
        serializer.save(driver=self.request.user.driver_profile)

    def perform_update(self, serializer):
        serializer.save(driver=self.request.user.driver_profile)


class VehicleCategoryModelViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = VehicleCategorySerializer
    queryset = VehicleCategory.objects.all()


from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.html import escape


class OrderListJson(BaseDatatableView):
    # The model we're going to show
    model = Vehicle

    # define the columns that will be returned
    columns = ['driver', 'registration_number', 'capacity', 'category']

    # define column names that will be used in sorting
    # order is important and should be same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    order_columns = ['driver', '', '', 'category']

    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 500

    def render_column(self, row, column):
        # We want to render user as a custom column
        if column == 'driver':
            # escape HTML for security reasons
            return escape('{0} {1}'.format(row.driver.user.full_name, row.driver.user.phone_number))
        else:
            return super(OrderListJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        # use parameters passed in GET request to filter queryset

        # simple example:
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(registration_number__istartswith=search)

        # more advanced example using extra parameters
        # filter_customer = self.request.GET.get('customer', None)
        #
        # if filter_customer:
        #     customer_parts = filter_customer.split(' ')
        #     qs_params = None
        #     for part in customer_parts:
        #         q = Q(customer_firstname__istartswith=part) | Q(customer_lastname__istartswith=part)
        #         qs_params = qs_params | q if qs_params else q
        #     qs = qs.filter(qs_params)
        return qs
