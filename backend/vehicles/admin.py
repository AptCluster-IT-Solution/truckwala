from django.contrib import admin

from vehicles.models import Vehicle, VehicleCategory, VehicleImage, VehicleDocument


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ["registration_number", "capacity", "category", "driver"]


@admin.register(VehicleCategory)
class VehicleCategoryAdmin(admin.ModelAdmin):
    list_display = ["title"]

admin.site.register(VehicleImage)
admin.site.register(VehicleDocument)
