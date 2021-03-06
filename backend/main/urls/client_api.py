from django.urls import path, include, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import DefaultRouter

from bookings.api import (
    CustomerAdModelViewSet,
    DriverAdModelViewSet,
    CustomerAdBidModelViewSet,
    DriverAdBidModelViewSet, BookingModelViewSet, TransactionModelViewSet,
)
from notifications.api import NotificationModelViewSet
from vehicles.api import (
    VehicleModelViewSet,
    VehicleCategoryModelViewSet,
)
from users.api import (
    RegisterAPI,
    UserViewset,
    LoginAPI,
    DriverViewset,
    CustomerViewset,
)
from knox import views as knox_views

router = DefaultRouter()
urlpatterns = []
admin_urlpatterns = [
    path("login/", LoginAPI.as_view(), name="login"),
]
# -------------- auth app view sets --------------
urlpatterns += [
    path("", include((admin_urlpatterns, "admin"), namespace="admin"))
]
urlpatterns += [
    path("register/", RegisterAPI.as_view()),
    path("user/", UserViewset.as_view({"get": "retrieve"})),
    path("logout/", knox_views.LogoutView.as_view(), name="knox_logout"),
]
router.register("users", UserViewset)
router.register("drivers", DriverViewset)
router.register("customers", CustomerViewset)
# -------------- auth app view sets --------------

# -------------- vehicles app view sets --------------
router.register("vehicles", VehicleModelViewSet, basename="Vehicle")
router.register("vehicle-categories", VehicleCategoryModelViewSet, basename="VehicleCategory")
# -------------- vehicles app view sets --------------

# -------------- bookings app view sets --------------
router.register("bookings", BookingModelViewSet, basename="Booking")
router.register("customer-ads", CustomerAdModelViewSet, basename="CustomerAd")
router.register("customer-ad-bids", CustomerAdBidModelViewSet, basename="CustomerAdBid")
router.register("driver-ads", DriverAdModelViewSet, basename="DriverAd")
router.register("driver-ad-bids", DriverAdBidModelViewSet, basename="DriverAdBid")
router.register("transactions", TransactionModelViewSet, basename="Transaction")
# -------------- bookings app view sets --------------

# -------------- notifications app view sets --------------
router.register("notifications", NotificationModelViewSet, basename="Notification")
# -------------- notifications app view sets --------------

urlpatterns += router.urls

schema_view = get_schema_view(
    openapi.Info(
        title="Truck Booking API",
        default_version="v1",
        description="Doc for client API",
        contact=openapi.Contact(email="zephyrr2722@gmail.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[path("", include(urlpatterns))],
)

urlpatterns += [
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),
]
