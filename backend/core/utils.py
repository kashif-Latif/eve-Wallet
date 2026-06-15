import random
import string
from decimal import Decimal

from django.db import transaction


def generate_wallet_number():
    """
    Generate a unique 12-digit wallet number.
    Ensures uniqueness by checking against existing wallet numbers.
    """
    from apps.wallets.models import Wallet

    while True:
        wallet_number = ''.join(random.choices(string.digits, k=12))
        if not Wallet.objects.filter(wallet_number=wallet_number).exists():
            return wallet_number


def generate_reference_number():
    """
    Generate a unique reference number for transactions.
    Format: TXN + 12 random alphanumeric characters.
    Ensures uniqueness by checking against existing reference numbers.
    """
    from apps.transactions.models import Transaction

    while True:
        chars = string.ascii_uppercase + string.digits
        reference_number = 'TXN' + ''.join(random.choices(chars, k=12))
        if not Transaction.objects.filter(reference_number=reference_number).exists():
            return reference_number


def generate_refund_reference():
    """
    Generate a unique reference number for refunds.
    Format: REF + 12 random alphanumeric characters.
    """
    from apps.refunds.models import Refund

    while True:
        chars = string.ascii_uppercase + string.digits
        reference_number = 'REF' + ''.join(random.choices(chars, k=12))
        if not Refund.objects.filter(reason__contains=reference_number).exists():
            return reference_number


def send_notification(user, title, message, notification_type='system'):
    """
    Send a notification to a user.
    Creates a Notification record in the database.

    Args:
        user: The User instance to notify
        title: Notification title
        message: Notification message body
        notification_type: One of 'transaction', 'refund', 'system', 'security', 'promotional'

    Returns:
        The created Notification instance
    """
    from apps.notifications.models import Notification

    valid_types = ['transaction', 'refund', 'system', 'security', 'promotional']
    if notification_type not in valid_types:
        notification_type = 'system'

    notification = Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
    )
    return notification


def calculate_fee(amount, transaction_type='transfer'):
    """
    Calculate the transaction fee based on amount and transaction type.
    Fee structure:
    - Transfers: 1.5% (minimum $0.50, maximum $25.00)
    - Deposits: Free
    - Withdrawals: 1.0% (minimum $1.00, maximum $10.00)
    - Refunds: Free

    Args:
        amount: The transaction amount (Decimal or float)
        transaction_type: The type of transaction

    Returns:
        Decimal: The calculated fee
    """
    amount = Decimal(str(amount))

    if transaction_type == 'transfer':
        fee = amount * Decimal('0.015')  # 1.5%
        fee = max(fee, Decimal('0.50'))  # Minimum $0.50
        fee = min(fee, Decimal('25.00'))  # Maximum $25.00
    elif transaction_type == 'withdrawal':
        fee = amount * Decimal('0.01')  # 1.0%
        fee = max(fee, Decimal('1.00'))  # Minimum $1.00
        fee = min(fee, Decimal('10.00'))  # Maximum $10.00
    else:
        fee = Decimal('0.00')

    return fee.quantize(Decimal('0.01'))


def validate_wallet_limits(wallet, amount):
    """
    Validate that a transaction does not exceed the wallet's daily and monthly limits.

    Args:
        wallet: The Wallet instance
        amount: The transaction amount

    Returns:
        tuple: (is_valid, error_message)
    """
    from apps.transactions.models import Transaction
    from django.utils import timezone

    amount = Decimal(str(amount))
    today = timezone.now().date()
    first_of_month = today.replace(day=1)

    # Check daily limit
    daily_total = Transaction.objects.filter(
        sender_wallet=wallet,
        status='completed',
        created_at__date=today,
    ).exclude(
        transaction_type='deposit'
    ).values_list('amount', flat=True)

    daily_sum = sum(daily_total) if daily_total else Decimal('0.00')
    if daily_sum + amount > wallet.daily_limit:
        remaining = wallet.daily_limit - daily_sum
        return False, f"Daily limit exceeded. Remaining daily limit: ${remaining:.2f}"

    # Check monthly limit
    monthly_total = Transaction.objects.filter(
        sender_wallet=wallet,
        status='completed',
        created_at__date__gte=first_of_month,
    ).exclude(
        transaction_type='deposit'
    ).values_list('amount', flat=True)

    monthly_sum = sum(monthly_total) if monthly_total else Decimal('0.00')
    if monthly_sum + amount > wallet.monthly_limit:
        remaining = wallet.monthly_limit - monthly_sum
        return False, f"Monthly limit exceeded. Remaining monthly limit: ${remaining:.2f}"

    return True, None


class WalletError(Exception):
    """Base exception for wallet operations."""
    pass


class InsufficientFundsError(WalletError):
    """Raised when a wallet has insufficient funds."""
    pass


class WalletFrozenError(WalletError):
    """Raised when attempting to transact with a frozen wallet."""
    pass


class WalletInactiveError(WalletError):
    """Raised when attempting to transact with an inactive wallet."""
    pass


class TransactionLimitError(WalletError):
    """Raised when a transaction exceeds wallet limits."""
    pass


class InvalidTransactionError(WalletError):
    """Raised when a transaction is invalid."""
    pass


class RefundError(Exception):
    """Base exception for refund operations."""
    pass


def custom_exception_handler(exc, context):
    """
    Custom exception handler for Django REST Framework.
    Ensures all error responses follow the consistent format:
    {success: False, message: str, data: {errors: ...}}
    """
    from rest_framework.views import exception_handler
    from rest_framework.response import Response
    from rest_framework import status

    # Call DRF's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Handle DRF exceptions
        if isinstance(response.data, dict):
            detail = response.data.pop('detail', None)
            if detail:
                message = str(detail)
            else:
                # Validation errors or field errors
                message = 'Validation error'
                errors = {}
                for key, value in response.data.items():
                    if isinstance(value, list):
                        errors[key] = value
                    else:
                        errors[key] = [str(value)]

                response.data = {
                    'success': False,
                    'message': message,
                    'data': {'errors': errors} if errors else None,
                }
                return response
        elif isinstance(response.data, list):
            message = str(response.data[0]) if response.data else 'An error occurred'
            response.data = {
                'success': False,
                'message': message,
                'data': None,
            }
            return response

        response.data = {
            'success': False,
            'message': str(detail) if detail else 'An error occurred',
            'data': None,
        }
    else:
        # Handle non-DRF exceptions (our custom exceptions)
        if isinstance(exc, (WalletError, RefundError)):
            response = Response({
                'success': False,
                'message': str(exc),
                'data': None,
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Unhandled exception
            response = Response({
                'success': False,
                'message': 'An unexpected error occurred.',
                'data': None,
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response
