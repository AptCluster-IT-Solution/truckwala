from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.reverse import reverse

from bookings.models import CustomerAd, DriverAd, CustomerAdBid, DriverAdBid, Booking, Transaction
from users.serializers import UserSerializer
from vehicles.models import VehicleCategory
from vehicles.serializers import VehicleSerializer


class CustomerAdSerializer(serializers.ModelSerializer):
    class BidSerializer(serializers.ModelSerializer):
        bidder = UserSerializer(source="bidder.user", read_only=True)
        vehicle = VehicleSerializer(read_only=True)

        class Meta:
            model = CustomerAdBid
            fields = "__all__"
            ref_name = "CustomerAdBidSerializer"

    poster = UserSerializer(source="poster.user", required=False)
    acceptor = UserSerializer(source="acceptor.user", required=False)
    bids = BidSerializer(read_only=True, many=True)

    class Meta:
        model = CustomerAd
        fields = "__all__"


class VehicleCategoryWithAdsSerializer(serializers.ModelSerializer):
    class CustomerAdSerializer(serializers.ModelSerializer):
        poster = UserSerializer(source="poster.user", required=False)
        acceptor = UserSerializer(source="acceptor.user", required=False)

        class Meta:
            model = CustomerAd
            fields = "__all__"

    ads = serializers.SerializerMethodField()

    @staticmethod
    def get_ads(obj):
        return CustomerAdSerializer(
            CustomerAd.objects.filter(
                vehicle_category_id=obj.id,
                start_time__gte=timezone.now(),
                acceptor__isnull=True,
            ),
            many=True, read_only=True
        ).data

    class Meta:
        model = VehicleCategory
        fields = "__all__"


class CustomerAdBidSerializer(serializers.ModelSerializer):
    class AdSerializer(serializers.ModelSerializer):
        poster = UserSerializer(source="poster.user", required=False)
        acceptor = UserSerializer(source="acceptor.user", required=False)

        class Meta:
            model = CustomerAd
            fields = "__all__"
            ref_name = "CustomerAdSerializer"

    ad = AdSerializer(read_only=True)
    ad_id = serializers.CharField(write_only=True, required=False)
    bidder = UserSerializer(source="bidder.user", read_only=True)
    bidder_id = serializers.CharField(write_only=True, required=False)
    vehicle = VehicleSerializer(read_only=True)
    vehicle_id = serializers.CharField(write_only=True, required=False)
    is_accepted = serializers.BooleanField(read_only=True)

    class Meta:
        model = CustomerAdBid
        fields = "__all__"

    def create(self, validated_data):
        if validated_data.get("vehicle_id") is None:
            try:
                validated_data["vehicle_id"] = self.context.get("request").user.driver_profile.vehicles.filter(
                    category=CustomerAd.objects.get(id=validated_data.get("ad_id")).vehicle_category
                ).first().id
            except (ObjectDoesNotExist, AttributeError) as e:
                raise PermissionDenied({"msg": "You dont have a vehicle of required category."})
        return super().create(validated_data)


class VehicleCategoryWithAdsForCustomerSerializer(serializers.ModelSerializer):
    class DriverAdSerializer(serializers.ModelSerializer):
        poster = UserSerializer(source="poster.user", required=False)
        acceptor = UserSerializer(source="acceptor.user", required=False)

        class Meta:
            model = DriverAd
            fields = "__all__"

    ads = serializers.SerializerMethodField()

    @staticmethod
    def get_ads(obj):
        return DriverAdSerializer(
            DriverAd.objects.filter(
                vehicle__category_id=obj.id,
                start_time__gte=timezone.now(),
                acceptor__isnull=True,
            ),
            many=True, read_only=True
        ).data

    class Meta:
        model = VehicleCategory
        fields = "__all__"


class DriverAdSerializer(serializers.ModelSerializer):
    class BidSerializer(serializers.ModelSerializer):
        bidder = UserSerializer(source="bidder.user", read_only=True)

        class Meta:
            model = DriverAdBid
            fields = "__all__"

    poster = UserSerializer(source="poster.user", required=False)
    acceptor = UserSerializer(source="acceptor.user", required=False)
    vehicle = VehicleSerializer(read_only=True)
    vehicle_id = serializers.CharField(write_only=True, required=False)
    bids = BidSerializer(read_only=True, many=True)

    class Meta:
        model = DriverAd
        fields = "__all__"

    def create(self, validated_data):
        return super().create(validated_data)


class DriverAdBidSerializer(serializers.ModelSerializer):
    class AdSerializer(serializers.ModelSerializer):
        poster = UserSerializer(source="poster.user", required=False)
        acceptor = UserSerializer(source="acceptor.user", required=False)
        vehicle = VehicleSerializer(read_only=True)
        vehicle_id = serializers.CharField(write_only=True)

        class Meta:
            model = DriverAd
            fields = "__all__"

    ad = AdSerializer(required=False)
    ad_id = serializers.CharField(write_only=True, required=False)
    bidder = UserSerializer(source="bidder.user", required=False)
    bidder_id = serializers.CharField(write_only=True, required=False)
    is_accepted = serializers.BooleanField(read_only=True)

    class Meta:
        model = DriverAdBid
        fields = "__all__"


class BookingSerializer(serializers.ModelSerializer):
    ad = serializers.SerializerMethodField()
    cost = serializers.SerializerMethodField()
    vehicle = serializers.SerializerMethodField()
    invoice = serializers.SerializerMethodField(read_only=True)

    def get_invoice(self, obj):
        return reverse(f"Booking-invoice", args=(obj.id,), request=self.context.get("request"))

    def get_ad(self, obj):
        if obj.driver_ad:
            return DriverAdSerializer(obj.ad, context=self.context).data
        else:
            return CustomerAdSerializer(obj.ad, context=self.context).data

    @staticmethod
    def get_cost(obj):
        return obj.cost

    def get_vehicle(self, obj):
        return VehicleSerializer(obj.vehicle, context=self.context).data

    class Meta:
        model = Booking
        fields = ['id', 'ad', 'status', "cost", "vehicle", "invoice_image", "invoice"]


class BookingCompleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'invoice_image']

    def update(self, instance, validated_data):
        instance.invoice_image = validated_data.get('invoice_image')
        instance.status = Booking.FULFILLED
        instance.save()
        return instance


class TransactionSerializer(serializers.ModelSerializer):
    customer = serializers.StringRelatedField(source="booking.customer")
    driver = serializers.StringRelatedField()
    commission = serializers.SerializerMethodField()

    @staticmethod
    def get_commission(obj):
        if obj.booking:
            return obj.booking.vehicle.category.commission * obj.booking.cost / 100
        return None

    class Meta:
        model = Transaction
        fields = ['id', 'customer', 'driver', 'amount', 'commission', 'date']
