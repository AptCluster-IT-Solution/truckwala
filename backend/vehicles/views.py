from rest_framework import viewsets
from rest_framework.response import Response

from vehicles.models import Vehicle, VehicleCategory
from vehicles.serializers import VehicleSerializer, VehicleCategorySerializer


class VehicleModelViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleSerializer
    queryset = Vehicle.objects.all()

    def perform_create(self, serializer):
        serializer.save(driver=self.request.user.driver_profile)

    def perform_update(self, serializer):
        serializer.save(driver=self.request.user.driver_profile)


class VehicleCategoryModelViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = VehicleCategorySerializer
    queryset = VehicleCategory.objects.all()
