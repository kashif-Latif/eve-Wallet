from rest_framework import serializers
from decimal import Decimal

from .models import Refund
from apps.transactions.serializers import TransactionListSerializer
from apps.accounts.serializers import UserMinimalSerializer
from apps.accounts.validators import validate_amount


class RefundSerializer(serializers.ModelSerializer):
    """
    Full serializer for the Refund model.
    """

    transaction_details = TransactionListSerializer(source='transaction', read_only=True)
    requested_by_details = UserMinimalSerializer(source='requested_by', read_only=True)
    processed_by_details = UserMinimalSerializer(source='processed_by', read_only=True)

    class Meta:
        model = Refund
        fields = [
            'id', 'transaction', 'requested_by', 'reason', 'status',
            'admin_note', 'processed_by', 'amount', 'transaction_details',
            'requested_by_details', 'processed_by_details',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'status', 'processed_by', 'created_at', 'updated_at'
        ]


class RefundListSerializer(serializers.ModelSerializer):
    """
    Serializer for refund list views (minimal data).
    """

    transaction_reference = serializers.CharField(
        source='transaction.reference_number', read_only=True
    )
    requested_by_username = serializers.CharField(
        source='requested_by.username', read_only=True
    )
    processed_by_username = serializers.CharField(
        source='processed_by.username', read_only=True, default=None
    )

    class Meta:
        model = Refund
        fields = [
            'id', 'transaction', 'transaction_reference',
            'requested_by', 'requested_by_username',
            'reason', 'status', 'admin_note', 'amount',
            'processed_by', 'processed_by_username',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields


class RequestRefundSerializer(serializers.Serializer):
    """
    Serializer for requesting a refund.
    """

    transaction_id = serializers.IntegerField(
        help_text="ID of the transaction to refund"
    )
    reason = serializers.CharField(
        min_length=10,
        max_length=1000,
        help_text="Reason for the refund request"
    )
    amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False,
        help_text="Partial refund amount (defaults to full transaction amount)"
    )

    def validate_transaction_id(self, value):
        from apps.transactions.models import Transaction

        try:
            transaction = Transaction.objects.get(pk=value)
        except Transaction.DoesNotExist:
            raise serializers.ValidationError('Transaction not found.')

        if transaction.status != 'completed':
            raise serializers.ValidationError(
                'Only completed transactions can be refunded.'
            )

        if transaction.transaction_type == 'refund':
            raise serializers.ValidationError(
                'Cannot request a refund for a refund transaction.'
            )

        # Check if there's already a pending/approved refund for this transaction
        existing_refund = Refund.objects.filter(
            transaction=transaction,
            status__in=['pending', 'approved']
        ).exists()
        if existing_refund:
            raise serializers.ValidationError(
                'A refund request for this transaction is already pending or approved.'
            )

        self.context['transaction'] = transaction
        return value

    def validate_amount(self, value):
        if value is not None:
            validate_amount(value)
        return value

    def validate(self, attrs):
        request = self.context.get('request')
        transaction = self.context.get('transaction')

        # Only the sender can request a refund
        if transaction.sender_wallet.user != request.user and request.user.role not in ('admin', 'superadmin'):
            raise serializers.ValidationError(
                'Only the sender of the transaction can request a refund.'
            )

        # Validate partial refund amount
        amount = attrs.get('amount')
        if amount is not None:
            if Decimal(str(amount)) > transaction.amount:
                raise serializers.ValidationError(
                    f'Refund amount cannot exceed transaction amount (${transaction.amount:.2f}).'
                )

        return attrs


class ProcessRefundSerializer(serializers.Serializer):
    """
    Serializer for processing (approving/rejecting) a refund.
    Admin-only operation.
    """

    action = serializers.ChoiceField(
        choices=['approve', 'reject'],
        help_text="Approve or reject the refund"
    )
    admin_note = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
        help_text="Admin note about the decision"
    )


class CompleteRefundSerializer(serializers.Serializer):
    """
    Serializer for completing a refund (returns money).
    Admin-only operation.
    """

    admin_note = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
        help_text="Admin note about the completion"
    )
