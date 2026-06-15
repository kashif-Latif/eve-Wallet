from rest_framework.permissions import BasePermission


class IsTransactionParticipant(BasePermission):
    """
    Permission class that allows access to transaction participants
    (sender or receiver) or admin users.
    """

    def has_object_permission(self, request, view, obj):
        # Admin can access all transactions
        if request.user.role in ('admin', 'superadmin'):
            return True

        # Check if user is sender or receiver
        return (
            obj.sender_wallet.user == request.user or
            obj.receiver_wallet.user == request.user
        )


class IsSenderOrAdmin(BasePermission):
    """
    Permission class that only allows the sender or admin to modify a transaction.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.role in ('admin', 'superadmin'):
            return True
        return obj.sender_wallet.user == request.user
