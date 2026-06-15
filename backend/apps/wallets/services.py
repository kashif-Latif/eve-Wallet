from decimal import Decimal
from django.db import transaction as db_transaction

from apps.wallets.models import Wallet
from core.utils import (
    send_notification,
    InsufficientFundsError,
    WalletFrozenError,
    WalletInactiveError,
    TransactionLimitError,
    validate_wallet_limits,
)


class WalletService:
    """
    Service layer for wallet operations.
    Encapsulates business logic for wallet management.
    """

    @staticmethod
    def create_wallet(user):
        """
        Create a new wallet for a user with $1000 initial balance.
        Called via signal on user registration.

        Args:
            user: The User instance to create a wallet for

        Returns:
            The created Wallet instance
        """
        wallet = Wallet.objects.create(
            user=user,
            balance=Decimal('1000.00'),
        )

        # Send welcome notification
        send_notification(
            user=user,
            title='Wallet Created',
            message=f'Your wallet has been created with number {wallet.wallet_number}. '
                    f'Initial balance: $1,000.00',
            notification_type='system',
        )

        return wallet

    @staticmethod
    def freeze_wallet(wallet, admin_user, reason=''):
        """
        Freeze a wallet. Admin-only operation.

        Args:
            wallet: The Wallet instance to freeze
            admin_user: The admin performing the action
            reason: Reason for freezing

        Returns:
            The updated Wallet instance
        """
        if wallet.is_frozen:
            raise ValueError('Wallet is already frozen.')

        wallet.is_frozen = True
        wallet.save()

        # Notify the wallet owner
        send_notification(
            user=wallet.user,
            title='Wallet Frozen',
            message=f'Your wallet {wallet.wallet_number} has been frozen. '
                    f'Reason: {reason or "No reason provided"}. '
                    f'Please contact support for assistance.',
            notification_type='security',
        )

        return wallet

    @staticmethod
    def unfreeze_wallet(wallet, admin_user, reason=''):
        """
        Unfreeze a wallet. Admin-only operation.

        Args:
            wallet: The Wallet instance to unfreeze
            admin_user: The admin performing the action
            reason: Reason for unfreezing

        Returns:
            The updated Wallet instance
        """
        if not wallet.is_frozen:
            raise ValueError('Wallet is not frozen.')

        wallet.is_frozen = False
        wallet.save()

        # Notify the wallet owner
        send_notification(
            user=wallet.user,
            title='Wallet Unfrozen',
            message=f'Your wallet {wallet.wallet_number} has been unfrozen. '
                    f'You can now perform transactions.',
            notification_type='security',
        )

        return wallet

    @staticmethod
    def validate_transaction(wallet, amount):
        """
        Validate that a wallet can perform a transaction.

        Args:
            wallet: The Wallet instance
            amount: The transaction amount

        Raises:
            WalletFrozenError: If the wallet is frozen
            WalletInactiveError: If the wallet is inactive
            InsufficientFundsError: If the wallet has insufficient funds
            TransactionLimitError: If the transaction exceeds limits
        """
        amount = Decimal(str(amount))

        if wallet.is_frozen:
            raise WalletFrozenError(
                f'Wallet {wallet.wallet_number} is frozen. Cannot perform transactions.'
            )

        if not wallet.is_active:
            raise WalletInactiveError(
                f'Wallet {wallet.wallet_number} is inactive. Cannot perform transactions.'
            )

        if not wallet.has_sufficient_funds(amount):
            raise InsufficientFundsError(
                f'Insufficient funds. Available balance: ${wallet.balance:.2f}, '
                f'Requested amount: ${amount:.2f}'
            )

        # Check wallet limits
        is_valid, error_message = validate_wallet_limits(wallet, amount)
        if not is_valid:
            raise TransactionLimitError(error_message)

    @staticmethod
    def deposit(wallet, amount):
        """
        Add funds to a wallet.

        Args:
            wallet: The Wallet instance
            amount: The amount to deposit

        Returns:
            The updated Wallet instance
        """
        amount = Decimal(str(amount))

        if amount <= 0:
            raise ValueError('Deposit amount must be greater than zero.')

        wallet.balance += amount
        wallet.save()

        # Send notification
        send_notification(
            user=wallet.user,
            title='Deposit Received',
            message=f'${amount:.2f} has been deposited to your wallet. '
                    f'New balance: ${wallet.balance:.2f}',
            notification_type='transaction',
        )

        return wallet

    @staticmethod
    def withdraw(wallet, amount):
        """
        Withdraw funds from a wallet.

        Args:
            wallet: The Wallet instance
            amount: The amount to withdraw

        Returns:
            The updated Wallet instance
        """
        amount = Decimal(str(amount))

        if amount <= 0:
            raise ValueError('Withdrawal amount must be greater than zero.')

        # Validate the transaction
        WalletService.validate_transaction(wallet, amount)

        wallet.balance -= amount
        wallet.save()

        # Send notification
        send_notification(
            user=wallet.user,
            title='Withdrawal Processed',
            message=f'${amount:.2f} has been withdrawn from your wallet. '
                    f'New balance: ${wallet.balance:.2f}',
            notification_type='transaction',
        )

        return wallet
