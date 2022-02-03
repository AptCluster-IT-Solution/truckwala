from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import User, Driver, Customer, DriverDocument, CustomerDocument


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id", "full_name", "phone_number", "password",
            "gender", "date_of_birth", "email",
            "address", "pan_number",
        )
        extra_kwargs = {"password": {"write_only": True}}


class PasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField()

    class Meta:
        model = User
        fields = ("password",)


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(required=False)
    new_password = serializers.CharField()

    class Meta:
        model = User
        fields = ("old_password", "new_password",)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    @staticmethod
    def validate(data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    @staticmethod
    def get_role(obj):
        if hasattr(obj, "driver_profile"):
            return "driver"
        return "customer"

    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "email",
            "gender",
            "date_of_birth",
            "phone_number",
            "address",
            "pan_number",
            "role",
        ]


class DriverSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Driver
        fields = "__all__"


class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Customer
        fields = "__all__"


class DocumentUploadSerializer(serializers.Serializer):  # noqa
    role = serializers.CharField()
    file = serializers.FileField()
    profile_id = serializers.CharField()

    def create(self, validated_data):
        if validated_data.get("role")[0].upper() == "D":
            return DriverDocument.objects.create(
                driver_id=validated_data.get("profile_id"),
                image=validated_data.get("file"),
            )
        elif validated_data.get("role")[0].upper() == "C":
            return CustomerDocument.objects.create(
                customer_id=validated_data.get("profile_id"),
                image=validated_data.get("file"),
            )
        else:
            raise ValidationError({"role": "role required or not properly defined."})
