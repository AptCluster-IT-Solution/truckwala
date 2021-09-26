from django.urls import path
from django.contrib import admin

from main.admin import admin_site
import users.views as users_views


# admin.autodiscover()
urlpatterns = [
    path("verification/", users_views.handle_user_verification, name="verification"),
    path("", admin_site.urls),
]
