from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django_datatables_view.base_datatable_view import BaseDatatableView
from rest_framework.decorators import api_view

from main.custom.permissions import StaffUserRequiredMixin
from .models import Customer, Driver, User


@staff_member_required
@api_view(["GET"])
def handle_user_verification(request):
    if not request.META.get("HTTP_REFERER"):
        return redirect("/")
    user_type = request.GET.get("user_type")
    user_id = request.GET.get("user_id")
    response = bool(int(request.GET.get("response")))

    if user_type[0].lower() == "d":
        instance = Driver.objects.get(pk=user_id)
    else:
        instance = Customer.objects.get(pk=user_id)

    instance.is_verified = response
    instance.save(update_fields=["is_verified"])

    return redirect(request.META["HTTP_REFERER"])


@staff_member_required
@api_view(["GET"])
def view_driver_documents(request):
    if not request.META.get("HTTP_REFERER"):
        return redirect("/")
    user_type = request.GET.get("user_type")
    user_id = request.GET.get("user_id")
    response = bool(int(request.GET.get("response")))

    if user_type[0].lower() == "d":
        instance = Driver.objects.get(pk=user_id)
    else:
        instance = Customer.objects.get(pk=user_id)

    instance.is_verified = response
    instance.save(update_fields=["is_verified"])

    return redirect(request.META["HTTP_REFERER"])
