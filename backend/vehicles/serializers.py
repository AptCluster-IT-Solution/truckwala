from django.db import transaction
from rest_framework import serializers

from .models import Vehicle, VehicleImage, VehicleCategory


class ImageUrlField(serializers.RelatedField):  # noqa
    def to_representation(self, instance):
        url = instance.image.url
        request = self.context.get('request', None)
        if request is not None:
            return request.build_absolute_uri(url)
        return url


class VehicleSerializer(serializers.ModelSerializer):
    driver = serializers.StringRelatedField(required=False)
    image_set = serializers.ListField(write_only=True)
    images = ImageUrlField(many=True, read_only=True)

    class Meta:
        model = Vehicle
        fields = "__all__"

    def create(self, validated_data):
        with transaction.atomic():
            image_set = validated_data.pop('image_set', [])
            instance = Vehicle.objects.create(**validated_data)
            for image in image_set:
                VehicleImage.objects.create(vehicle=instance, image=image)
            return instance


class VehicleCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleCategory
        fields = "__all__"
