from rest_framework import serializers

from .models import Vehicle


class VehicleSerializer(serializers.ModelSerializer):
    driver = serializers.StringRelatedField(required=False)

    class Meta:
        model = Vehicle
        fields = "__all__"
