from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission

SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')

class IsDeliveryAdminUser(BasePermission):
    """
    Allows access only to delivery admin users.
    """

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return bool(request.user and request.user.role == 'delivery_admin') or bool(request.user and request.user.role == 'admin')
        else:
            raise AuthenticationFailed(detail="Authentication credentials were not provided")
    
class IsAdmin(BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return bool(request.user and request.user.role == 'admin')
        else:
            raise AuthenticationFailed(detail="Authentication credentials were not provided")
        
        
class IsAdminOrReadOnly(BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return bool(request.user and request.user.role == 'admin')
        elif request.method in SAFE_METHODS:
            return True
        else:
            raise AuthenticationFailed(detail="Authentication credentials were not provided")
        
        
    