from rest_framework import serializers
from decimal import Decimal

from .models import Wallet
from apps.accounts.serializers import UserMinimalSerializer


class WalletSerializer(serializers.ModelSerializer):
    """
    Full serializer for the Wallet model.
    """

    user = UserMinimalSerializer(read_only=True)
    available_balance = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Wallet
        fields = [
            'id', 'user', 'wallet_number', 'balance', 'available_balance',
            'is_active', 'is_frozen', 'currency', 'daily_limit',
            'monthly_limit', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'wallet_number', 'balance', 'is_active',
            'is_frozen', 'created_at', 'updated_at'
        ]


class WalletBalanceSerializer(serializers.ModelSerializer):
    """
    Serializer for wallet balance information.
    """

    available_balance = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Wallet
        fields = [
            'wallet_number', 'balance', 'available_balance',
            'currency', 'is_active', 'is_frozen'
        ]
        read_only_fields = fields


class WalletMinimalSerializer(serializers.ModelSerializer):
    """
    Minimal serializer for nested wallet representations.
    """

    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Wallet
        fields = ['id', 'wallet_number', 'balance', 'username']
        read_only_fields = fields


class FreezeWalletSerializer(serializers.Serializer):
    """
    Serializer for freezing/unfreezing a wallet.
    Admin-only operation.
    """

    action = serializers.ChoiceField(choices=['freeze', 'unfreeze'])
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
        help_text="Reason for freezing/unfreezing the wallet"
    )


class UpdateWalletLimitsSerializer(serializers.ModelSerializer):
    """
    Serializer for updating wallet limits (admin only).
    """

    class Meta:
        model = Wallet
        fields = ['daily_limit', 'monthly_limit']

    def validate_daily_limit(self, value):
        if value <= 0:
            raise serializers.ValidationError('Daily limit must be greater than zero.')
        if value > Decimal('1000000'):
            raise serializers.ValidationError('Daily limit cannot exceed $1,000,000.')
        return value

    def validate_monthly_limit(self, value):
        if value <= 0:
            raise serializers.ValidationError('Monthly limit must be greater than zero.')
        if value > Decimal('10000000'):
            raise serializers.ValidationError('Monthly limit cannot exceed $10,000,000.')
        return value
