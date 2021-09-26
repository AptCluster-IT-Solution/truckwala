from django.contrib import admin
from main.admin import admin_site, admin_register

from vehicles.models import Vehicle, VehicleCategory


@admin_register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ["registration_number", "capacity", "category", "driver"]

    def has_add_permission(self, request):
        return False


@admin_register(VehicleCategory)
class VehicleCategoryAdmin(admin.ModelAdmin):
    list_display = ["title"]
