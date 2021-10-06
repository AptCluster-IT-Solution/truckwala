from django.contrib import admin

from vehicles.models import Vehicle, VehicleCategory


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ["registration_number", "capacity", "category", "driver"]


@admin.register(VehicleCategory)
class VehicleCategoryAdmin(admin.ModelAdmin):
    list_display = ["title"]
