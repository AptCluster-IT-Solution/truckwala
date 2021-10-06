from django.contrib.auth.decorators import login_required
from django.urls import path
from django.contrib import admin
from django.contrib.auth import views as auth_views

from main.admin import admin_site
import users.views as users_views
import admin_panel.views as admin_views

# admin.autodiscover()
from vehicles.views import OrderListJson

urlpatterns = [
    # path('accounts/login/', users_views.LoginView.as_view(template_name='users/login.html'), name="login"),
    path("verification/", users_views.handle_user_verification, name="verification"),
    path('my/datatable/data/', login_required(OrderListJson.as_view()), name='order_list_json'),

    path('drivers/', admin_views.DriversPage.as_view(), name="drivers_page"),
    path('drivers_list_data/', admin_views.DriversListJson.as_view(), name="drivers_list_json"),
    path('customers/', admin_views.CustomersPage.as_view(), name="customers_page"),
    path('customers_list_data/', admin_views.CustomersListJson.as_view(), name="customers_list_json"),

    path('vehicles/', admin_views.VehiclesPage.as_view(), name="vehicles_page"),
    path('vehicles_list_data/', admin_views.VehiclesListJson.as_view(), name="vehicles_list_json"),

    path('driver-ads/', admin_views.DriverAdsPage.as_view(), name="driver_ads_page"),
    path('driver_ads_list_data/', admin_views.DriverAdsListJson.as_view(), name="driver_ads_list_json"),
    path('customer-ads/', admin_views.CustomerAdsPage.as_view(), name="customer_ads_page"),
    path('customer_ads_list_data/', admin_views.CustomerAdsListJson.as_view(), name="customer_ads_list_json"),

    path('bookings/', admin_views.BookingsPage.as_view(), name="bookings_page"),
    path('bookings_list_data/', admin_views.BookingsListJson.as_view(), name="bookings_list_json"),
    path('transactions/', admin_views.TransactionsPage.as_view(), name="transactions_page"),
    path('transactions_list_data/', admin_views.TransactionsListJson.as_view(), name="transactions_list_json"),

    path("", admin_views.Dashboard.as_view(), name="dashboard"),
    path("", admin_site.urls),
]
