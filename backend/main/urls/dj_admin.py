from django.contrib.auth.decorators import login_required
from django.urls import path
from django.contrib import admin
from django.contrib.auth import views as auth_views

import users.views as users_views
import admin_panel.views as admin_views

# admin.autodiscover()
from vehicles.views import OrderListJson

urlpatterns = [
    # path('accounts/login/', users_views.LoginView.as_view(template_name='users/login.html'), name="login"),
    path("verification/", users_views.handle_user_verification, name="verification"),
    path('my/datatable/data/', login_required(OrderListJson.as_view()), name='order_list_json'),

    path('unverified-drivers/', admin_views.UnverifiedDriversPage.as_view(), name="unverified_drivers_page"),
    path('unverified_drivers_list_data/', admin_views.UnverifiedDriversListJson.as_view(),
         name="unverified_drivers_list_json"),
    path('drivers/', admin_views.DriversPage.as_view(), name="drivers_page"),
    path('drivers/payment/', admin_views.driver_payment, name="drivers_payment"),
    path('drivers_list_data/', admin_views.DriversListJson.as_view(), name="drivers_list_json"),
    path('customers/', admin_views.CustomersPage.as_view(), name="customers_page"),
    path('customers_list_data/', admin_views.CustomersListJson.as_view(), name="customers_list_json"),

    path('vehicles/', admin_views.VehiclesPage.as_view(), name="vehicles_page"),
    path('vehicles_list_data/', admin_views.VehiclesListJson.as_view(), name="vehicles_list_json"),
    path('vehicle-categories/', admin_views.VehicleCategoriesPage.as_view(), name="vehicle_categories_page"),
    path('vehicle-categories/<int:pk>', admin_views.VehicleCategoriesPage.as_view(), name="vehicle_categories_update"),
    path('vehicle_categories_list_data/', admin_views.VehicleCategoriesListJson.as_view(),
         name="vehicle_categories_list_json"),

    path('driver-ads/', admin_views.DriverAdsPage.as_view(), name="driver_ads_page"),
    path('driver_ads_list_data/', admin_views.DriverAdsListJson.as_view(), name="driver_ads_list_json"),
    path('customer-ads/', admin_views.CustomerAdsPage.as_view(), name="customer_ads_page"),
    path('customer_ads_list_data/', admin_views.CustomerAdsListJson.as_view(), name="customer_ads_list_json"),

    path('bookings/', admin_views.BookingsPage.as_view(), name="bookings_page"),
    path('bookings_list_data/', admin_views.BookingsListJson.as_view(), name="bookings_list_json"),
    path('customer-transactions/', admin_views.CustomerToDriverTransactionsPage.as_view(),
         name="customer_to_driver_transactions_page"),
    path('customer_transactions_list_data/', admin_views.CustomerToDriverTransactionsListJson.as_view(),
         name="customer_to_driver_transactions_list_json"),
    path('driver-transactions/', admin_views.DriverToAdminTransactionsPage.as_view(),
         name="driver_to_admin_transactions_page"),
    path('driver_transactions_list_data/', admin_views.DriverToAdminTransactionsListJson.as_view(),
         name="driver_to_admin_transactions_list_json"),

    path("", admin_views.Dashboard.as_view(), name="dashboard"),
    path("", admin.site.urls),
]
