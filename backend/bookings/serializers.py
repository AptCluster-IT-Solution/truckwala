from rest_framework import serializers

from bookings.models import CustomerAd, DriverAd
from users.serializers import UserSerializer, CustomerSerializer, DriverSerializer


class CustomerAdSerializer(serializers.ModelSerializer):
    poster = UserSerializer(source="poster.user")
    acceptor = serializers.StringRelatedField(required=False)

    class Meta:
        model = CustomerAd
        fields = "__all__"


class DriverAdSerializer(serializers.ModelSerializer):
    poster = UserSerializer(source="poster.user")
    acceptor = serializers.StringRelatedField(required=False)

    class Meta:
        model = DriverAd
        fields = "__all__"
