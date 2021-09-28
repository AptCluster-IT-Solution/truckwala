from rest_framework import serializers

from bookings.models import CustomerAd, DriverAd


class CustomerAdSerializer(serializers.ModelSerializer):
    poster = serializers.StringRelatedField(required=False)
    acceptor = serializers.StringRelatedField(required=False)

    class Meta:
        model = CustomerAd
        fields = "__all__"


class DriverAdSerializer(serializers.ModelSerializer):
    poster = serializers.StringRelatedField(required=False)
    acceptor = serializers.StringRelatedField(required=False)

    class Meta:
        model = DriverAd
        fields = "__all__"
