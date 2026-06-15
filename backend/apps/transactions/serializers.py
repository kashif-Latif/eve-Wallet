from rest_framework import serializers
from decimal import Decimal

from .models import Transaction
from apps.wallets.serializers import WalletMinimalSerializer
from apps.accounts.validators import validate_amount
from core.utils import calculate_fee


class TransactionSerializer(serializers.ModelSerializer):
    """
    Full serializer for the Transaction model.
    """

    sender_wallet_details = WalletMinimalSerializer(source='sender_wallet', read_only=True)
    receiver_wallet_details = WalletMinimalSerializer(source='receiver_wallet', read_only=True)
    total_amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Transaction
        fields = [
            'id', 'sender_wallet', 'receiver_wallet', 'amount', 'fee',
            'total_amount', 'transaction_type', 'status', 'reference_number',
            'description', 'sender_wallet_details', 'receiver_wallet_details',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'fee', 'status', 'reference_number',
            'created_at', 'updated_at'
        ]


class TransactionListSerializer(serializers.ModelSerializer):
    """
    Serializer for transaction list views (minimal data).
    """

    sender_username = serializers.CharField(
        source='sender_wallet.user.username', read_only=True
    )
    receiver_username = serializers.CharField(
        source='receiver_wallet.user.username', read_only=True
    )
    total_amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Transaction
        fields = [
            'id', 'reference_number', 'sender_wallet', 'receiver_wallet',
            'sender_username', 'receiver_username', 'amount', 'fee',
            'total_amount', 'transaction_type', 'status',
            'description', 'created_at'
        ]
        read_only_fields = fields


class SendMoneySerializer(serializers.Serializer):
    """
    Serializer for sending money between wallets.
    Requires PIN verification token before processing.
    Uses transaction.atomic() for safe transfers.
    """

    receiver_wallet_number = serializers.CharField(
        max_length=12,
        help_text="The 12-digit wallet number to send money to"
    )
    amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Amount to send"
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
        help_text="Description or note for the transaction"
    )
    pin_verification_token = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Token from PIN verification (required if PIN is set)"
    )

    def validate_amount(self, value):
        validate_amount(value)
        return value

    def validate_receiver_wallet_number(self, value):
        from apps.wallets.models import Wallet

        try:
            wallet = Wallet.objects.get(wallet_number=value)
        except Wallet.DoesNotExist:
            raise serializers.ValidationError(
                f'Wallet with number {value} does not exist.'
            )

        if not wallet.is_active:
            raise serializers.ValidationError(
                'The receiver wallet is inactive.'
            )

        if wallet.is_frozen:
            raise serializers.ValidationError(
                'The receiver wallet is frozen and cannot receive funds.'
            )

        return value

    def validate(self, attrs):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError('Authentication required.')

        # Verify PIN if user has set one
        if request.user.pin_set:
            pin_token = attrs.get('pin_verification_token', '')
            if not pin_token:
                raise serializers.ValidationError({
                    'pin_verification_token': 'PIN verification required. Please verify your PIN first.'
                })
            from django.core.cache import cache
            cache_key = f'pin_verified_{request.user.id}'
            cached_token = cache.get(cache_key)
            if not cached_token or cached_token != pin_token:
                raise serializers.ValidationError({
                    'pin_verification_token': 'Invalid or expired PIN verification. Please verify your PIN again.'
                })
            # Consume the token (one-time use)
            cache.delete(cache_key)

        # Get sender's wallet
        from apps.wallets.models import Wallet
        try:
            sender_wallet = Wallet.objects.get(user=request.user)
        except Wallet.DoesNotExist:
            raise serializers.ValidationError('Sender wallet not found.')

        amount = attrs['amount']

        # Validate sender wallet
        if not sender_wallet.is_active:
            raise serializers.ValidationError('Your wallet is inactive.')

        if sender_wallet.is_frozen:
            raise serializers.ValidationError('Your wallet is frozen. Cannot send money.')

        # Check if sending to self
        receiver_wallet = Wallet.objects.get(wallet_number=attrs['receiver_wallet_number'])
        if sender_wallet.id == receiver_wallet.id:
            raise serializers.ValidationError('Cannot send money to your own wallet.')

        # Check sufficient funds (amount + fee)
        fee = calculate_fee(amount, 'transfer')
        total_deduction = amount + fee

        if sender_wallet.balance < total_deduction:
            raise serializers.ValidationError(
                f'Insufficient funds. Required: ${total_deduction:.2f} '
                f'(Amount: ${amount:.2f} + Fee: ${fee:.2f}), '
                f'Available: ${sender_wallet.balance:.2f}'
            )

        # Store in context for use in the view
        self.context['sender_wallet'] = sender_wallet
        self.context['receiver_wallet'] = receiver_wallet
        self.context['fee'] = fee

        return attrs


class DepositSerializer(serializers.Serializer):
    """
    Serializer for depositing money into a wallet.
    """

    amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Amount to deposit"
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
        help_text="Description for the deposit"
    )

    def validate_amount(self, value):
        validate_amount(value)
        if Decimal(str(value)) > Decimal('100000'):
            raise serializers.ValidationError(
                'Maximum deposit amount is $100,000 per transaction.'
            )
        return value


class CancelTransactionSerializer(serializers.Serializer):
    """
    Serializer for cancelling a pending transaction.
    """

    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
        help_text="Reason for cancellation"
    )
