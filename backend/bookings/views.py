from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from bookings.models import CustomerAd, DriverAd, Booking
from bookings.serializers import CustomerAdSerializer, DriverAdSerializer
from main.custom.permissions import (
    IsPosterOrReadOnly,
    IsCustomer,
    ActionBasedPermission,
    IsDriver,
)


class CustomerAdModelViewSet(viewsets.ModelViewSet):
    queryset = CustomerAd.objects.all()
    serializer_class = CustomerAdSerializer
    permission_classes = [ActionBasedPermission]
    action_permissions = {
        IsPosterOrReadOnly: ["update", "partial_update", "destroy", "list", "retrieve"],
        IsCustomer: ["create"],
        IsDriver: ["accept"],
    }

    def perform_create(self, serializer):
        serializer.save(poster=self.request.user.customer_profile)

    @action(detail=True, methods=["patch"])
    def accept(self, request, pk=None):
        ad = self.get_object()
        ad.acceptor = request.user.driver_profile
        ad.save(update_fields=["acceptor"])

        ad.booking.status = Booking.ACCEPTED
        ad.booking.save(update_fields=["status"])

        return Response({"acceptor": "ad accepted"})


class DriverAdModelViewSet(viewsets.ModelViewSet):
    queryset = DriverAd.objects.all()
    serializer_class = DriverAdSerializer
    permission_classes = [ActionBasedPermission]
    action_permissions = {
        IsDriver: ["create"],
        IsPosterOrReadOnly: ["update", "partial_update", "destroy", "list", "retrieve"],
        IsCustomer: ["accept"],
    }

    def perform_create(self, serializer):
        serializer.save(poster=self.request.user.driver_profile)

    @action(detail=True, methods=["patch"])
    def accept(self, request, pk=None):
        ad = self.get_object()
        ad.acceptor = request.user.customer_profile
        ad.save(update_fields=["acceptor"])

        ad.booking.status = Booking.ACCEPTED
        ad.booking.save(update_fields=["status"])

        return Response({"acceptor": "ad accepted"})
