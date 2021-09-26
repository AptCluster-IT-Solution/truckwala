from functools import partial
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.contrib.admin.apps import AdminConfig

from django.apps import apps
from django.urls import NoReverseMatch, reverse
from django.utils.text import capfirst

from main.helpers.weekdays import weekdays


class MyAdminConfig(AdminConfig):
    default_site = "main.admin.MyAdminSite"


class MyAdminSite(AdminSite):
    index_title = "Dashboard"

    def index(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}
        extra_context["weekdays"] = weekdays()
        return super().index(request, extra_context)


admin_site = MyAdminSite(name="Dashboard Admin")

admin_register = partial(admin.register, site=admin_site)
