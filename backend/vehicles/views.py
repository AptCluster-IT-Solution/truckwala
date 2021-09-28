from rest_framework import viewsets
from rest_framework.response import Response

from main.custom.permissions import ActionBasedPermission, IsPosterOrReadOnly, IsDriver
from vehicles.models import Vehicle, VehicleCategory
from vehicles.serializers import VehicleSerializer, VehicleCategorySerializer


class VehicleModelViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleSerializer
    queryset = Vehicle.objects.all()
    permission_classes = [ActionBasedPermission]
    action_permissions = {
        IsPosterOrReadOnly: ["update", "partial_update", "destroy", "list", "retrieve"],
        IsDriver: ["create"],
    }

    def perform_create(self, serializer):
        serializer.save(driver=self.request.user.driver_profile)

    def perform_update(self, serializer):
        serializer.save(driver=self.request.user.driver_profile)


class VehicleCategoryModelViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = VehicleCategorySerializer
    queryset = VehicleCategory.objects.all()
