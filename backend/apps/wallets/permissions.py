from rest_framework.permissions import BasePermission


class IsWalletOwner(BasePermission):
    """
    Permission class that only allows the owner of the wallet.
    """

    def has_object_permission(self, request, view, obj):
        # Admin can access all wallets
        if request.user.role in ('admin', 'superadmin'):
            return True
        return obj.user == request.user


class IsWalletOwnerOrAdmin(BasePermission):
    """
    Permission class that allows the wallet owner or admin users.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.role in ('admin', 'superadmin'):
            return True
        return obj.user == request.user


class CanTransact(BasePermission):
    """
    Permission class that checks if the wallet can perform transactions.
    """

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'can_transact'):
            return obj.can_transact()
        return True
