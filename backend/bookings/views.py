from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from bookings.models import CustomerAd, DriverAd, CustomerAdBid, DriverAdBid, Booking
from bookings.serializers import CustomerAdSerializer, DriverAdSerializer, CustomerAdBidSerializer, \
    DriverAdBidSerializer
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
        IsDriver: ["bid"],
    }
    filterset_fields = ['start_place', 'end_place']

    def perform_create(self, serializer):
        serializer.save(poster=self.request.user.customer_profile)

    @action(detail=True, methods=["patch"])
    def bid(self, request, pk=None):
        ad = self.get_object()
        serializer = CustomerAdBidSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(ad_id=ad.id, bidder_id=request.user.driver_profile.id)
            return Response(serializer.data)
        else:
            raise ValidationError(serializer.errors)


class CustomerAdBidModelViewSet(viewsets.ModelViewSet):
    queryset = CustomerAdBid.objects.all()
    serializer_class = CustomerAdBidSerializer
    permission_classes = [ActionBasedPermission]
    action_permissions = {
        IsPosterOrReadOnly: ["accept", "reject", "update", "partial_update", "destroy", "list", "retrieve"],
        IsDriver: ["create"],
    }

    @action(detail=True, methods=['PATCH'])
    def accept(self, request, pk=None):
        bid = self.get_object()
        ad: CustomerAd = bid.ad
        bid.is_accepted = True
        bid.save(update_fields=['is_accepted'])

        ad.acceptor = bid.bidder
        ad.save(update_fields=['acceptor'])

        ad.booking.status = Booking.ACCEPTED
        ad.booking.save(update_fields=['status'])

        return Response({"bid": "bid accepted"})

    @action(detail=True, methods=['PATCH'])
    def reject(self, request, pk=None):
        bid = self.get_object()
        bid.is_accepted = False
        bid.save(update_fields=['is_accepted'])

        return Response({"bid": "bid rejected"})


class DriverAdModelViewSet(viewsets.ModelViewSet):
    queryset = DriverAd.objects.all()
    serializer_class = DriverAdSerializer
    permission_classes = [ActionBasedPermission]
    action_permissions = {
        IsDriver: ["create"],
        IsPosterOrReadOnly: ["update", "partial_update", "destroy", "list", "retrieve"],
        IsCustomer: ["bid"],
    }
    filterset_fields = ['start_place', 'end_place', 'vehicle__category']

    def perform_create(self, serializer):
        serializer.save(poster=self.request.user.driver_profile)

    @action(detail=True, methods=["patch"])
    def bid(self, request, pk=None):
        ad = self.get_object()
        serializer = DriverAdBidSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(ad_id=ad.id, bidder_id=request.user.customer_profile.id)
            return Response(serializer.data)
        else:
            raise ValidationError(serializer.errors)


class DriverAdBidModelViewSet(viewsets.ModelViewSet):
    queryset = DriverAdBid.objects.all()
    serializer_class = DriverAdBidSerializer
    permission_classes = [ActionBasedPermission]
    action_permissions = {
        IsPosterOrReadOnly: ["accept", "reject", "update", "partial_update", "destroy", "list", "retrieve"],
        IsCustomer: ["create"],
    }

    @action(detail=True, methods=['PATCH'])
    def accept(self, request, pk=None):
        bid = self.get_object()
        ad: DriverAd = bid.ad
        bid.is_accepted = True
        bid.save(update_fields=['is_accepted'])

        ad.acceptor = bid.bidder
        ad.save(update_fields=['acceptor'])

        ad.booking.status = Booking.ACCEPTED
        ad.booking.save(update_fields=['status'])

        return Response({"bid": "bid accepted"})

    @action(detail=True, methods=['PATCH'])
    def reject(self, request, pk=None):
        bid = self.get_object()
        bid.is_accepted = False
        bid.save(update_fields=['is_accepted'])

        return Response({"bid": "bid rejected"})