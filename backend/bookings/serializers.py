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
    driver_ad = DriverAdSerializer()
    driver_bid = DriverAdBidSerializer()
    customer_ad = CustomerAdSerializer()
    customer_bid = CustomerAdBidSerializer()
    cost = serializers.SerializerMethodField()

    @staticmethod
    def get_cost(obj):
        return obj.cost

    class Meta:
        model = Booking
        fields = ['id', 'driver_ad', 'driver_bid', 'customer_ad', "customer_bid", 'status'
                  # 'vehicle', 'cost', 'status', 'start_place', 'end_place'
            , "cost"]


class BookingCompleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'invoice_image']

    def update(self, instance, validated_data):
        instance.invoice_image = validated_data.get('invoice_image')
        instance.status = Booking.FULFILLED
        instance.save()
        return instance
