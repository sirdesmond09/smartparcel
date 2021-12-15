from rest_framework.permissions import BasePermission


class IsDeliveryAdminUser(BasePermission):
    """
    Allows access only to delivery admin users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.role == 'delivery_admin')