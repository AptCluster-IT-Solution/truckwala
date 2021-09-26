from rest_framework import viewsets
from rest_framework.response import Response

from vehicles.models import Vehicle
from vehicles.serializers import VehicleSerializer


class VehicleModelViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleSerializer
    queryset = Vehicle.objects.all()

    def perform_create(self, serializer):
        serializer.save(driver=self.request.user.driver_profile)

    def perform_update(self, serializer):
        serializer.save(driver=self.request.user.driver_profile)
