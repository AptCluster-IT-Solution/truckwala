from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import permissions
from rest_framework.permissions import AllowAny


class StaffUserRequiredMixin(LoginRequiredMixin):
    """Verify that the current user is authenticated and is super user."""

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        return self.handle_no_permission()


class ActionBasedPermission(AllowAny):
    """
    Grant or deny access to a view, based on a mapping in view.action_permissions
    """

    def has_permission(self, request, view):
        for klass, actions in getattr(view, "action_permissions", {}).items():
            if view.action in actions:
                return klass().has_permission(request, view)
        return False

    def has_object_permission(self, request, view, obj):
        for klass, actions in getattr(view, "action_permissions", {}).items():
            if view.action in actions:
                return klass().has_object_permission(request, view, obj)
        return False


class IsCustomer(permissions.BasePermission):
    """
    Allows access only to customer.
    """

    def has_permission(self, request, view):
        is_permitted = False
        if request.user and request.user.is_authenticated:
            if request.user.is_superuser:
                is_permitted = True
            elif hasattr(request.user, "customer_profile"):
                if request.user.customer_profile.is_verified:
                    is_permitted = True

        return is_permitted


class IsDriver(permissions.BasePermission):
    """
    Allows access only to Driver.
    """

    def has_permission(self, request, view):
        is_permitted = False
        if request.user and request.user.is_authenticated:
            if request.user.is_superuser:
                is_permitted = True
            elif hasattr(request.user, "driver_profile"):
                if request.user.driver_profile.is_verified:
                    is_permitted = True

        return is_permitted


class IsPosterOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `poster` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        if hasattr(obj, 'poster'):
            return obj.poster.user == request.user
        elif hasattr(obj, 'ad') and hasattr(obj.ad, "poster"):
            return obj.ad.poster.user == request.user
        return False
