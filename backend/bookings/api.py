from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from bookings.models import CustomerAd, DriverAd, CustomerAdBid, DriverAdBid, Booking, Transaction
from bookings.serializers import CustomerAdSerializer, DriverAdSerializer, CustomerAdBidSerializer, \
    DriverAdBidSerializer, BookingSerializer, BookingCompleteSerializer, TransactionSerializer, \
    VehicleCategoryWithAdsSerializer, VehicleCategoryWithAdsForCustomerSerializer
from main.custom.permissions import (
    IsPosterOrReadOnly,
    IsCustomer,
    ActionBasedPermission,
    IsVerifiedDriver,
)
from main.custom.utils import render_to_pdf
from vehicles.models import VehicleCategory


class CustomerAdModelViewSet(viewsets.ModelViewSet):
    queryset = CustomerAd.objects.all()
    serializer_class = CustomerAdSerializer
    permission_classes = [ActionBasedPermission]
    action_permissions = {
        IsCustomer: ["create"],
        IsVerifiedDriver: ["bid", "for_me"],
        IsPosterOrReadOnly: ["update", "partial_update", "destroy", "list", "retrieve", "me"],
    }
    filterset_fields = ['start_place', 'end_place', 'vehicle_category']

    def get_queryset(self):
        if self.action in ['list']:
            qs = CustomerAd.objects.exclude(bids__is_accepted=True)
            if hasattr(self.request.user, "driver_profile"):
                try:
                    category = self.request.user.driver_profile.vehicles.first().category
                except ObjectDoesNotExist:
                    category = None
                qs = qs.filter(vehicle_category=category)
            return qs
        return CustomerAd.objects.all()

    def perform_destroy(self, instance):
        if self.get_object().booking.status not in [Booking.PENDING]:
            raise ValidationError({"msg": "Sorry, this order has been accepted."})
        instance.delete()

    def perform_create(self, serializer):
        serializer.save(poster=self.request.user.customer_profile)

    @action(detail=False, methods=["GET"])
    def me(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).filter(poster__user=self.request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["GET"], url_path="for-me")
    def for_me(self, request, *args, **kwargs):
        queryset = VehicleCategory.objects.filter(
            vehicles__driver__user=request.user,
            customer_ads__start_time__gte=timezone.now()
        ).distinct()
        serializer = VehicleCategoryWithAdsSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["patch"])
    def bid(self, request, pk=None):
        ad = self.get_object()
        serializer = CustomerAdBidSerializer(data=request.data, context=self.get_serializer_context())
        if serializer.is_valid(raise_exception=True):
            serializer.save(ad_id=ad.id, bidder_id=request.user.driver_profile.id)
            return Response(serializer.data)
        else:
            raise ValidationError(serializer.errors)


class CustomerAdBidModelViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerAdBidSerializer
    permission_classes = [ActionBasedPermission]
    action_permissions = {
        IsVerifiedDriver: ["create"],
        IsPosterOrReadOnly: ["accept", "reject", "update", "partial_update", "destroy", "list", "retrieve", "me"],
    }

    def get_queryset(self):
        if self.request.user.is_authenticated:
            if self.action in ['accept', 'reject']:
                return CustomerAdBid.objects.filter(ad__poster__user=self.request.user)
            return CustomerAdBid.objects.filter(bidder__user=self.request.user)
        return CustomerAdBid.objects.none()

    def perform_create(self, serializer):
        serializer.save(is_accepted=True)

    @action(detail=False, methods=["GET"])
    def me(self, request, *args, **kwargs):
        queryset = CustomerAdBid.objects.filter(ad__poster__user=self.request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['PATCH'])
    def accept(self, request, pk=None):
        bid = self.get_object()
        ad: CustomerAd = bid.ad
        bid.is_accepted = True
        bid.save(update_fields=['is_accepted'])

        ad.acceptor = bid.bidder
        ad.save(update_fields=['acceptor'])

        ad.booking.status = Booking.ACCEPTED
        ad.booking.customer_bid = bid
        ad.booking.save(update_fields=['status', 'customer_bid'])

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
        IsVerifiedDriver: ["create"],
        IsCustomer: ["bid", "for_me", ],
        IsPosterOrReadOnly: ["update", "partial_update", "destroy", "list", "retrieve", "me"],
    }
    filterset_fields = ['start_place', 'end_place', 'vehicle__category']

    def get_queryset(self):
        if self.action in ['list']:
            return DriverAd.objects.exclude(bids__is_accepted=True)
        return DriverAd.objects.all()

    def perform_destroy(self, instance):
        if self.get_object().booking.status not in [Booking.PENDING]:
            raise ValidationError({"msg": "Sorry, this order has been accepted."})
        instance.delete()

    def perform_create(self, serializer):
        if DriverAd.objects.filter(poster__user=self.request.user, acceptor__isnull=True).count():
            raise ValidationError({"msg": "Unaccepted Ad already exists"})

        try:
            vehicle = self.request.user.driver_profile.vehicles.first()
        except ObjectDoesNotExist:
            vehicle = None

        serializer.save(
            poster=self.request.user.driver_profile,
            vehicle=vehicle
        )

    @action(detail=False, methods=["GET"])
    def me(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).filter(poster__user=self.request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["GET"], url_path="for-me")
    def for_me(self, request, *args, **kwargs):
        queryset = VehicleCategory.objects.all()
        serializer = VehicleCategoryWithAdsForCustomerSerializer(queryset, many=True)
        return Response(serializer.data)

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
    serializer_class = DriverAdBidSerializer
    permission_classes = [ActionBasedPermission]
    action_permissions = {
        IsCustomer: ["create"],
        IsPosterOrReadOnly: ["accept", "reject", "update", "partial_update", "destroy", "list", "retrieve", "me"],
    }

    def get_queryset(self):
        if self.request.user.is_authenticated:
            if self.action in ['accept', 'reject']:
                return DriverAdBid.objects.filter(ad__poster__user=self.request.user)
            return DriverAdBid.objects.filter(bidder__user=self.request.user)
        return DriverAdBid.objects.none()

    def perform_create(self, serializer):
        serializer.save(is_accepted=True)

    @action(detail=False, methods=["GET"])
    def me(self, request, *args, **kwargs):
        queryset = DriverAdBid.objects.filter(ad__poster__user=self.request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['PATCH'])
    def accept(self, request, pk=None):
        bid = self.get_object()
        ad: DriverAd = bid.ad
        bid.is_accepted = True
        bid.save(update_fields=['is_accepted'])

        ad.acceptor = bid.bidder
        ad.save(update_fields=['acceptor'])

        ad.booking.status = Booking.ACCEPTED
        ad.booking.driver_bid = bid
        ad.booking.save(update_fields=['status', 'driver_bid'])

        return Response({"bid": "bid accepted"})

    @action(detail=True, methods=['PATCH'])
    def reject(self, request, pk=None):
        bid = self.get_object()
        bid.is_accepted = False
        bid.save(update_fields=['is_accepted'])

        return Response({"bid": "bid rejected"})


class BookingModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Booking.objects.filter(status__in=[Booking.ACCEPTED, Booking.FULFILLED])
    serializer_class = BookingSerializer
    permission_classes = [IsPosterOrReadOnly, IsAuthenticated]
    filterset_fields = ['status', ]

    @action(detail=False, methods=["GET"])
    def me(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).filter(
            Q(customer_ad__poster__user=self.request.user) | Q(customer_ad__acceptor__user=self.request.user) |
            Q(driver_ad__poster__user=self.request.user) | Q(driver_ad__acceptor__user=self.request.user)
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["GET"])
    def place_search(self, request, *args, **kwargs):
        q = request.GET.get("q")

        places = {
            *list(Booking.objects.filter(
                customer_ad__start_place__icontains=q
            ).values_list("customer_ad__start_place", flat=True)),
            *list(Booking.objects.filter(
                customer_ad__end_place__icontains=q
            ).values_list("customer_ad__end_place", flat=True)),
            *list(Booking.objects.filter(
                driver_ad__start_place__icontains=q
            ).values_list("driver_ad__start_place", flat=True)),
            *list(Booking.objects.filter(
                driver_ad__end_place__icontains=q
            ).values_list("driver_ad__end_place", flat=True))
        }

        return Response({"results": places})

    @action(detail=True, methods=['POST'], permission_classes=[IsPosterOrReadOnly, IsVerifiedDriver])
    def complete(self, request, pk=None):
        booking = self.get_object()
        serializer = BookingCompleteSerializer(instance=booking, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"booking": "booking fulfilled"})
        else:
            raise ValidationError(serializer.errors)

    @action(detail=True, methods=['GET'], permission_classes=[IsPosterOrReadOnly])
    def invoice(self, request, pk=None):
        booking = self.get_object()

        return render_to_pdf(
            'bookings/invoice.html',
            {"booking": booking},
            download=self.request.GET.get('is_pdf', False),
        )


class TransactionModelViewSet(ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [ActionBasedPermission]
    action_permissions = {
        IsVerifiedDriver: ["list", "retrieve"],
        IsAdminUser: ["accept", "reject", "update", "partial_update", "destroy", "list", "retrieve", "me"],
    }

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Transaction.objects.filter(driver__user=self.request.user)
        return Transaction.objects.none()
