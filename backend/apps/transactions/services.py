from decimal import Decimal
from django.db import transaction as db_transaction

from apps.transactions.models import Transaction
from apps.wallets.models import Wallet
from apps.wallets.services import WalletService
from core.utils import (
    calculate_fee,
    send_notification,
    generate_reference_number,
    InsufficientFundsError,
    WalletFrozenError,
    WalletInactiveError,
    TransactionLimitError,
    InvalidTransactionError,
    validate_wallet_limits,
)


class TransactionService:
    """
    Service layer for transaction operations.
    All money transfers use transaction.atomic() with rollback on failure.
    """

    @staticmethod
    @db_transaction.atomic
    def send_money(sender_wallet, receiver_wallet, amount, description='', fee=None):
        """
        Send money from one wallet to another.
        Uses transaction.atomic() for safe transfer with rollback on failure.

        Args:
            sender_wallet: The Wallet instance sending money
            receiver_wallet: The Wallet instance receiving money
            amount: The amount to send (Decimal)
            description: Optional description/note
            fee: Override fee amount (if None, calculated automatically)

        Returns:
            The created Transaction instance

        Raises:
            InsufficientFundsError: If sender has insufficient funds
            WalletFrozenError: If either wallet is frozen
            WalletInactiveError: If either wallet is inactive
            TransactionLimitError: If transaction exceeds limits
        """
        amount = Decimal(str(amount))

        # Validate sender wallet
        if sender_wallet.is_frozen:
            raise WalletFrozenError(
                f'Your wallet is frozen. Cannot send money.'
            )
        if not sender_wallet.is_active:
            raise WalletInactiveError(
                f'Your wallet is inactive. Cannot send money.'
            )

        # Validate receiver wallet
        if receiver_wallet.is_frozen:
            raise WalletFrozenError(
                f'Receiver wallet is frozen. Cannot receive money.'
            )
        if not receiver_wallet.is_active:
            raise WalletInactiveError(
                f'Receiver wallet is inactive. Cannot receive money.'
            )

        # Calculate fee if not provided
        if fee is None:
            fee = calculate_fee(amount, 'transfer')
        fee = Decimal(str(fee))

        # Total deduction from sender
        total_deduction = amount + fee

        # Check sufficient funds
        if sender_wallet.balance < total_deduction:
            raise InsufficientFundsError(
                f'Insufficient funds. Required: ${total_deduction:.2f}, '
                f'Available: ${sender_wallet.balance:.2f}'
            )

        # Check wallet limits
        is_valid, error_message = validate_wallet_limits(sender_wallet, amount)
        if not is_valid:
            raise TransactionLimitError(error_message)

        # Cannot send to self
        if sender_wallet.id == receiver_wallet.id:
            raise InvalidTransactionError('Cannot send money to your own wallet.')

        # Select related wallets with lock for update (prevent race conditions)
        sender_wallet_locked = Wallet.objects.select_for_update().get(pk=sender_wallet.pk)
        receiver_wallet_locked = Wallet.objects.select_for_update().get(pk=receiver_wallet.pk)

        # Double-check balance after lock
        if sender_wallet_locked.balance < total_deduction:
            raise InsufficientFundsError(
                f'Insufficient funds after lock. Required: ${total_deduction:.2f}, '
                f'Available: ${sender_wallet_locked.balance:.2f}'
            )

        # Create transaction record
        txn = Transaction.objects.create(
            sender_wallet=sender_wallet_locked,
            receiver_wallet=receiver_wallet_locked,
            amount=amount,
            fee=fee,
            transaction_type='transfer',
            status='completed',
            description=description or f'Transfer to wallet {receiver_wallet.wallet_number}',
        )

        # Deduct from sender (amount + fee)
        sender_wallet_locked.balance -= total_deduction
        sender_wallet_locked.save()

        # Add to receiver (amount only)
        receiver_wallet_locked.balance += amount
        receiver_wallet_locked.save()

        # Send notifications
        send_notification(
            user=sender_wallet.user,
            title='Money Sent',
            message=f'${amount:.2f} has been sent to {receiver_wallet.user.username}. '
                    f'Fee: ${fee:.2f}. New balance: ${sender_wallet_locked.balance:.2f}',
            notification_type='transaction',
        )
        send_notification(
            user=receiver_wallet.user,
            title='Money Received',
            message=f'${amount:.2f} has been received from {sender_wallet.user.username}. '
                    f'New balance: ${receiver_wallet_locked.balance:.2f}',
            notification_type='transaction',
        )

        return txn

    @staticmethod
    @db_transaction.atomic
    def deposit(wallet, amount, description=''):
        """
        Deposit money into a wallet.
        Creates a transaction record with the sender being the same wallet.

        Args:
            wallet: The Wallet instance to deposit into
            amount: The amount to deposit (Decimal)
            description: Optional description

        Returns:
            The created Transaction instance
        """
        amount = Decimal(str(amount))

        if amount <= 0:
            raise InvalidTransactionError('Deposit amount must be greater than zero.')

        if not wallet.is_active:
            raise WalletInactiveError('Wallet is inactive. Cannot deposit.')

        if wallet.is_frozen:
            raise WalletFrozenError('Wallet is frozen. Cannot deposit.')

        # Select wallet with lock
        wallet_locked = Wallet.objects.select_for_update().get(pk=wallet.pk)

        # Create transaction record (sender = receiver for deposits)
        txn = Transaction.objects.create(
            sender_wallet=wallet_locked,
            receiver_wallet=wallet_locked,
            amount=amount,
            fee=Decimal('0.00'),
            transaction_type='deposit',
            status='completed',
            description=description or f'Deposit to wallet {wallet.wallet_number}',
        )

        # Add to balance
        wallet_locked.balance += amount
        wallet_locked.save()

        # Send notification
        send_notification(
            user=wallet.user,
            title='Deposit Successful',
            message=f'${amount:.2f} has been deposited to your wallet. '
                    f'New balance: ${wallet_locked.balance:.2f}',
            notification_type='transaction',
        )

        return txn

    @staticmethod
    @db_transaction.atomic
    def withdraw(wallet, amount, description=''):
        """
        Withdraw money from a wallet.

        Args:
            wallet: The Wallet instance to withdraw from
            amount: The amount to withdraw (Decimal)
            description: Optional description

        Returns:
            The created Transaction instance
        """
        amount = Decimal(str(amount))

        if amount <= 0:
            raise InvalidTransactionError('Withdrawal amount must be greater than zero.')

        # Calculate fee
        fee = calculate_fee(amount, 'withdrawal')
        total_deduction = amount + fee

        # Validate wallet
        if wallet.is_frozen:
            raise WalletFrozenError('Wallet is frozen. Cannot withdraw.')
        if not wallet.is_active:
            raise WalletInactiveError('Wallet is inactive. Cannot withdraw.')

        # Select wallet with lock
        wallet_locked = Wallet.objects.select_for_update().get(pk=wallet.pk)

        # Check balance
        if wallet_locked.balance < total_deduction:
            raise InsufficientFundsError(
                f'Insufficient funds for withdrawal. Required: ${total_deduction:.2f} '
                f'(Amount: ${amount:.2f} + Fee: ${fee:.2f}), '
                f'Available: ${wallet_locked.balance:.2f}'
            )

        # Check limits
        is_valid, error_message = validate_wallet_limits(wallet_locked, amount)
        if not is_valid:
            raise TransactionLimitError(error_message)

        # Create transaction record (sender = receiver for withdrawals)
        txn = Transaction.objects.create(
            sender_wallet=wallet_locked,
            receiver_wallet=wallet_locked,
            amount=amount,
            fee=fee,
            transaction_type='withdrawal',
            status='completed',
            description=description or f'Withdrawal from wallet {wallet.wallet_number}',
        )

        # Deduct from balance
        wallet_locked.balance -= total_deduction
        wallet_locked.save()

        # Send notification
        send_notification(
            user=wallet.user,
            title='Withdrawal Successful',
            message=f'${amount:.2f} has been withdrawn from your wallet. '
                    f'Fee: ${fee:.2f}. New balance: ${wallet_locked.balance:.2f}',
            notification_type='transaction',
        )

        return txn

    @staticmethod
    @db_transaction.atomic
    def cancel_transaction(transaction, user):
        """
        Cancel a pending transaction.

        Args:
            transaction: The Transaction instance to cancel
            user: The user requesting cancellation

        Returns:
            The updated Transaction instance

        Raises:
            InvalidTransactionError: If the transaction cannot be cancelled
        """
        if transaction.status != 'pending':
            raise InvalidTransactionError(
                f'Cannot cancel a transaction with status "{transaction.status}". '
                f'Only pending transactions can be cancelled.'
            )

        # Only the sender can cancel
        if transaction.sender_wallet.user != user and user.role not in ('admin', 'superadmin'):
            raise InvalidTransactionError(
                'Only the sender or an admin can cancel a transaction.'
            )

        transaction.status = 'cancelled'
        transaction.save()

        # Send notifications
        send_notification(
            user=transaction.sender_wallet.user,
            title='Transaction Cancelled',
            message=f'Transaction {transaction.reference_number} has been cancelled.',
            notification_type='transaction',
        )
        if transaction.receiver_wallet.user != transaction.sender_wallet.user:
            send_notification(
                user=transaction.receiver_wallet.user,
                title='Incoming Transaction Cancelled',
                message=f'Transaction {transaction.reference_number} has been cancelled.',
                notification_type='transaction',
            )

        return transaction

    @staticmethod
    @db_transaction.atomic
    def process_refund(transaction, refund_amount=None):
        """
        Process a refund for a completed transaction.
        Returns the money from receiver back to sender.

        Args:
            transaction: The original Transaction instance to refund
            refund_amount: Optional partial refund amount (defaults to full amount)

        Returns:
            The refund Transaction instance
        """
        if transaction.status != 'completed':
            raise InvalidTransactionError(
                'Only completed transactions can be refunded.'
            )

        if refund_amount is None:
            refund_amount = transaction.amount
        else:
            refund_amount = Decimal(str(refund_amount))

        if refund_amount <= 0 or refund_amount > transaction.amount:
            raise InvalidTransactionError(
                f'Invalid refund amount. Must be between $0.01 and ${transaction.amount:.2f}'
            )

        # Lock wallets
        sender_wallet = Wallet.objects.select_for_update().get(
            pk=transaction.receiver_wallet.pk
        )
        receiver_wallet = Wallet.objects.select_for_update().get(
            pk=transaction.sender_wallet.pk
        )

        # Check if receiver has enough balance for refund
        if sender_wallet.balance < refund_amount:
            raise InsufficientFundsError(
                f'Cannot process refund. Receiver wallet has insufficient balance: '
                f'${sender_wallet.balance:.2f}, Refund amount: ${refund_amount:.2f}'
            )

        # Create refund transaction
        refund_txn = Transaction.objects.create(
            sender_wallet=sender_wallet,
            receiver_wallet=receiver_wallet,
            amount=refund_amount,
            fee=Decimal('0.00'),
            transaction_type='refund',
            status='completed',
            description=f'Refund for transaction {transaction.reference_number}',
        )

        # Transfer money back
        sender_wallet.balance -= refund_amount
        sender_wallet.save()

        receiver_wallet.balance += refund_amount
        receiver_wallet.save()

        # Send notifications
        send_notification(
            user=sender_wallet.user,
            title='Refund Processed',
            message=f'${refund_amount:.2f} has been refunded from your wallet for '
                    f'transaction {transaction.reference_number}. '
                    f'New balance: ${sender_wallet.balance:.2f}',
            notification_type='refund',
        )
        send_notification(
            user=receiver_wallet.user,
            title='Refund Received',
            message=f'${refund_amount:.2f} has been refunded to your wallet for '
                    f'transaction {transaction.reference_number}. '
                    f'New balance: ${receiver_wallet.balance:.2f}',
            notification_type='refund',
        )

        return refund_txn
