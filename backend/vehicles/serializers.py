from django.db import transaction
from rest_framework import serializers

from main.custom.fields import ImageUrlField
from .models import Vehicle, VehicleImage, VehicleCategory, VehicleDocument


class VehicleSerializer(serializers.ModelSerializer):
    driver = serializers.StringRelatedField(required=False)
    category = serializers.StringRelatedField()
    category_id = serializers.CharField(write_only=True)
    image_set = serializers.ListField(write_only=True)
    images = ImageUrlField(many=True, read_only=True)
    document_set = serializers.ListField(write_only=True)
    documents = ImageUrlField(many=True, read_only=True)

    class Meta:
        model = Vehicle
        fields = "__all__"

    def create(self, validated_data):
        with transaction.atomic():
            image_set = validated_data.pop('image_set', [])
            document_set = validated_data.pop('document_set', [])
            instance = Vehicle.objects.create(**validated_data)
            for image in image_set:
                VehicleImage.objects.create(vehicle=instance, image=image)
            for document in document_set:
                VehicleDocument.objects.create(vehicle=instance, image=document)
            return instance


class VehicleCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleCategory
        fields = "__all__"
