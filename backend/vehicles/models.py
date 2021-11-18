import os

from django.db import models

from users.models import Driver


class VehicleCategory(models.Model):
    title = models.CharField(max_length=255)
    commission = models.PositiveSmallIntegerField()
    image = models.ImageField(upload_to="categories/", null=True, blank=True)

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name_plural = "Vehicle Categories"


class Vehicle(models.Model):
    driver: Driver = models.ForeignKey(
        Driver, on_delete=models.CASCADE, related_name="vehicles"
    )
    registration_number = models.CharField(max_length=255, unique=True)
    capacity = models.PositiveIntegerField()
    category = models.ForeignKey(
        VehicleCategory, on_delete=models.CASCADE, related_name="vehicles"
    )

    def __str__(self):
        return str(self.registration_number)


def get_vehicle_image_path(_, filename):
    return os.path.join("images/vehicles/", filename)


class VehicleImage(models.Model):
    vehicle: Vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to=get_vehicle_image_path)

    def __str__(self):
        return self.vehicle.registration_number


def get_vehicle_document_path(_, filename):
    return os.path.join("images/documents/", filename)


class VehicleDocument(models.Model):
    vehicle: Vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name="documents"
    )
    image = models.ImageField(upload_to=get_vehicle_document_path)

    def __str__(self):
        return self.vehicle.registration_number
