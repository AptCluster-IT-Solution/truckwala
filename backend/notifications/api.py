from django.db.models import Q
from rest_framework import viewsets, permissions

from notifications.models import Notification
from notifications.serializers import NotificationSerializer


class NotificationModelViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Notification.objects.filter(Q(created_for__isnull=True) | Q(created_for=self.request.user.id))
        if hasattr(self.request.user, "driver_profile"):
            queryset = queryset.exclude(notification_type=Notification.DRIVER_AD)
        elif hasattr(self.request.user, "customer_profile"):
            queryset = queryset.exclude(notification_type=Notification.CUSTOMER_AD)

        return queryset
