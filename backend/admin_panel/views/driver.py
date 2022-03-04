from django.http import HttpResponse
from django.views.generic import DetailView

from users.models import Driver


class DriverProfile(DetailView):
    model = Driver
    context_object_name = 'driver'
    template_name = 'admin_panel/htmx/driver_detail.html'
