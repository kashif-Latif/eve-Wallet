from rest_framework.permissions import BasePermission


class IsOwnerOrAdmin(BasePermission):
    """
    Permission class that allows users to access their own resources
    or allows admins full access.
    """

    def has_object_permission(self, request, view, obj):
        # Admin users can access everything
        if request.user.role in ('admin', 'superadmin'):
            return True

        # Check if the object has a user attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user

        # Check if the object is the user itself
        if hasattr(obj, 'id') and hasattr(request.user, 'id'):
            return obj.id == request.user.id

        return False


class IsAdmin(BasePermission):
    """
    Permission class that only allows admin and superadmin users.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ('admin', 'superadmin')

    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_authenticated and request.user.role in ('admin', 'superadmin')


class IsSuperAdmin(BasePermission):
    """
    Permission class that only allows superadmin users.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'superadmin'


class IsVerifiedUser(BasePermission):
    """
    Permission class that only allows verified users.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_verified


class IsOwner(BasePermission):
    """
    Permission class that only allows the owner of the object.
    """

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return obj == request.user
