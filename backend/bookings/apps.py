from django.apps import AppConfig


class BookingConfig(AppConfig):
    name = "bookings"

    def ready(self):
        import bookings.signals
