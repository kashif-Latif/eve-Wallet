from rest_framework.permissions import BasePermission


class IsRefundRequesterOrAdmin(BasePermission):
    """
    Permission class that allows the refund requester or admin users.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.role in ('admin', 'superadmin'):
            return True
        return obj.requested_by == request.user


class IsAdminOnly(BasePermission):
    """
    Permission class that only allows admin users for refund processing.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ('admin', 'superadmin')

    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_authenticated and request.user.role in ('admin', 'superadmin')
