from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from main.admin import admin_site, admin_register
from .models import User, Driver, Customer


@admin_register(User)
class UserAdmin(BaseUserAdmin):
    add_fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        (
            _("Personal info"),
            {"fields": ("first_name", "last_name", "email", "gender")},
        ),
    )

    ordering = ("phone_number",)
    list_display = ["id", "phone_number", "date_joined", "last_login"]
    search_fields = ("phone_number", "first_name", "last_name", "email")

    # readonly_fields = ["email", "phone_number", "last_login", "date_joined"]
    exclude = ["username"]
    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        (
            _("Personal info"),
            {"fields": ("first_name", "last_name", "email", "gender")},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )


@admin_register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False


@admin_register(Driver)
class DriverAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False
