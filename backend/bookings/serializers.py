from rest_framework import serializers

from bookings.models import CustomerAd, DriverAd, CustomerAdBid, DriverAdBid, Booking
from users.serializers import UserSerializer, CustomerSerializer, DriverSerializer
from vehicles.serializers import VehicleSerializer


class CustomerAdSerializer(serializers.ModelSerializer):
    poster = UserSerializer(source="poster.user", required=False)
    acceptor = serializers.StringRelatedField(required=False)

    class Meta:
        model = CustomerAd
        fields = "__all__"


class CustomerAdBidSerializer(serializers.ModelSerializer):
    ad = CustomerAdSerializer(read_only=True)
    ad_id = serializers.CharField(write_only=True, required=False)
    bidder = UserSerializer(source="bidder.user", read_only=True)
    bidder_id = serializers.CharField(write_only=True, required=False)
    vehicle = VehicleSerializer(read_only=True)
    vehicle_id = serializers.CharField(write_only=True)

    class Meta:
        model = CustomerAdBid
        # fields = "__all__"
        exclude = ['is_accepted']


class DriverAdSerializer(serializers.ModelSerializer):
    poster = UserSerializer(source="poster.user", required=False)
    acceptor = serializers.StringRelatedField(required=False)
    vehicle = VehicleSerializer(read_only=True)
    vehicle_id = serializers.CharField(write_only=True)

    class Meta:
        model = DriverAd
        fields = "__all__"

    def create(self, validated_data):
        return super().create(validated_data)


class DriverAdBidSerializer(serializers.ModelSerializer):
    ad = DriverAdSerializer(required=False)
    ad_id = serializers.CharField(write_only=True, required=False)
    bidder = UserSerializer(source="bidder.user", required=False)
    bidder_id = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = DriverAdBid
        # fields = "__all__"
        exclude = ['is_accepted']


class BookingSerializer(serializers.ModelSerializer):
    ad = serializers.SerializerMethodField()
    cost = serializers.SerializerMethodField()
    vehicle = serializers.SerializerMethodField()

    @staticmethod
    def get_ad(obj):
        if obj.driver_ad:
            return DriverAdSerializer(obj.ad).data
        else:
            return CustomerAdSerializer(obj.ad).data

    @staticmethod
    def get_cost(obj):
        return obj.cost

    @staticmethod
    def get_vehicle(obj):
        return VehicleSerializer(obj.vehicle).data

    class Meta:
        model = Booking
        fields = ['id', 'ad', 'status', "cost", "vehicle"]


class BookingCompleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'invoice_image']

    def update(self, instance, validated_data):
        instance.invoice_image = validated_data.get('invoice_image')
        instance.status = Booking.FULFILLED
        instance.save()
        return instance
