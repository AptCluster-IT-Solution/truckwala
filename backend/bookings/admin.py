from django.contrib import admin
from main.admin import admin_site, admin_register

from bookings.models import CustomerAd, DriverAd, Booking


@admin_register(CustomerAd)
@admin_register(DriverAd)
@admin_register(Booking)
class AdAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False
