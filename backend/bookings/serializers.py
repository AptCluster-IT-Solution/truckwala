from rest_framework import serializers

from bookings.models import CustomerAd, DriverAd


class CustomerAdSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAd
        fields = "__all__"


class DriverAdSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverAd
        fields = "__all__"
