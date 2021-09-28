from django.apps import AppConfig


class NotificationConfig(AppConfig):
    name = "notifications"

    def ready(self):
        import notifications.signals
