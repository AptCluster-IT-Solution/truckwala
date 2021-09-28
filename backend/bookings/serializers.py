from rest_framework import serializers

from bookings.models import CustomerAd, DriverAd, CustomerAdBid, DriverAdBid
from users.serializers import UserSerializer, CustomerSerializer, DriverSerializer


class CustomerAdSerializer(serializers.ModelSerializer):
    poster = UserSerializer(source="poster.user")
    acceptor = serializers.StringRelatedField(required=False)

    class Meta:
        model = CustomerAd
        fields = "__all__"


class CustomerAdBidSerializer(serializers.ModelSerializer):
    ad = CustomerAdSerializer(read_only=True)
    ad_id = serializers.CharField(write_only=True, required=False)
    bidder = UserSerializer(source="bidder.user", read_only=True)
    bidder_id = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomerAdBid
        fields = "__all__"


class DriverAdSerializer(serializers.ModelSerializer):
    poster = UserSerializer(source="poster.user")
    acceptor = serializers.StringRelatedField(required=False)

    class Meta:
        model = DriverAd
        fields = "__all__"


class DriverAdBidSerializer(serializers.ModelSerializer):
    ad = DriverAdSerializer()
    ad_id = serializers.CharField(write_only=True, required=False)
    bidder = UserSerializer(source="bidder.user")
    bidder_id = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = DriverAdBid
        fields = "__all__"

