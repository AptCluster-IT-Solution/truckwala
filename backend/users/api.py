from django.db import transaction
from knox.models import AuthToken
from rest_framework import generics, permissions, status
from rest_framework.decorators import action, api_view
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.custom.permissions import IsDriver, IsCustomer
from main.custom.viewsets import ContextModelViewSet
from .models import Customer, Driver, User
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    LoginSerializer,
    PasswordSerializer,
    DriverSerializer,
    CustomerSerializer,
    DocumentUploadSerializer,
)


@api_view(["GET"])
def is_auth(request):
    if request.user.is_authenticated:
        return Response(UserSerializer(request.user).data)
    return Response({"msg": False})


def verification_request(request, user=None):
    if not user:
        user = request.user
    role = request.data.get("role")
    if not role or role[0].upper() not in ["D", "C"]:
        raise ValidationError({"role": "role required or not properly defined."})
    else:
        role = role[0].upper()
        if role == "D":
            model_class = Driver
        elif role == "C":
            model_class = Customer
        else:
            raise ValidationError({"role": "role required or not properly defined."})

    instance, _ = model_class.objects.get_or_create(user=user)
    if instance.is_verified is False:
        instance.is_verified = None
        instance.save(update_fields=["is_verified"])

    documents = request.FILES.getlist("documents")

    if len(documents):
        for file in documents:
            file_serializer = DocumentUploadSerializer(
                data={"role": role, "profile_id": instance.id, "file": file}
            )
            if file_serializer.is_valid():
                file_serializer.save()
            else:
                return 0
        return 1
    raise ValidationError({"documents": "documents is required"})


class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        with transaction.atomic():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            # setting created user's password
            password_serializer = PasswordSerializer(data=request.data)
            if password_serializer.is_valid():
                user.set_password(password_serializer.data["password"])
                user.save()

            verification_request(request, user)

            return Response(
                {
                    "user": UserSerializer(
                        user, context=self.get_serializer_context()
                    ).data,
                    "token": AuthToken.objects.create(user)[1],
                }
            )


class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer

    #    permission_classes = [permissions.AllowAny,]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        return Response(
            {
                "user": UserSerializer(
                    user, context=self.get_serializer_context()
                ).data,
                "token": AuthToken.objects.create(user)[1],
            }
        )


class UserViewset(ContextModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user

    @action(detail=True, methods=["post"])
    def set_password(self, request, pk=None):
        user = self.get_object()
        serializer = PasswordSerializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.data["password"])
            user.save()
            return Response({"status": "password set"})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["POST"], detail=False, permission_classes=[IsAuthenticated])
    def request(self, request, *args, **kwargs):
        verification_request(request)

        return Response({"request": "A verification request has been made."})


class DriverViewset(ContextModelViewSet):
    permission_classes = [IsDriver]
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    parser_classes = (MultiPartParser, FileUploadParser)

    def get_object(self):
        return self.request.user


class CustomerViewset(ContextModelViewSet):
    permission_classes = [IsCustomer]
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def get_object(self):
        return self.request.user