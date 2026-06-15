from decimal import Decimal
from django.db import transaction as db_transaction

from apps.refunds.models import Refund
from apps.transactions.services import TransactionService
from apps.wallets.models import Wallet
from core.utils import (
    send_notification,
    InvalidTransactionError,
    RefundError,
)


class RefundService:
    """
    Service layer for refund operations.
    Encapsulates business logic for refund management.
    """

    @staticmethod
    def request_refund(user, transaction, reason, amount=None):
        """
        Create a refund request.

        Args:
            user: The user requesting the refund
            transaction: The original Transaction instance
            reason: Reason for the refund
            amount: Optional partial refund amount (defaults to full amount)

        Returns:
            The created Refund instance

        Raises:
            InvalidTransactionError: If the transaction cannot be refunded
        """
        if transaction.status != 'completed':
            raise InvalidTransactionError(
                'Only completed transactions can be refunded.'
            )

        if transaction.transaction_type == 'refund':
            raise InvalidTransactionError(
                'Cannot request a refund for a refund transaction.'
            )

        # Check for existing pending/approved refunds
        existing = Refund.objects.filter(
            transaction=transaction,
            status__in=['pending', 'approved']
        ).exists()
        if existing:
            raise RefundError(
                'A refund request for this transaction is already pending or approved.'
            )

        # Set refund amount
        if amount is None:
            amount = transaction.amount
        else:
            amount = Decimal(str(amount))

        if amount <= 0 or amount > transaction.amount:
            raise RefundError(
                f'Invalid refund amount. Must be between $0.01 and ${transaction.amount:.2f}'
            )

        # Create refund request
        refund = Refund.objects.create(
            transaction=transaction,
            requested_by=user,
            reason=reason,
            amount=amount,
            status='pending',
        )

        # Send notification
        send_notification(
            user=user,
            title='Refund Requested',
            message=f'Your refund request for ${amount:.2f} (Transaction: {transaction.reference_number}) '
                    f'has been submitted and is pending review.',
            notification_type='refund',
        )

        return refund

    @staticmethod
    @db_transaction.atomic
    def process_refund(refund, admin_user, action, admin_note=''):
        """
        Process (approve or reject) a refund request.
        Admin-only operation.

        Args:
            refund: The Refund instance to process
            admin_user: The admin processing the refund
            action: 'approve' or 'reject'
            admin_note: Optional admin note

        Returns:
            The updated Refund instance

        Raises:
            RefundError: If the refund cannot be processed
        """
        if refund.status != 'pending':
            raise RefundError(
                f'Cannot process a refund with status "{refund.status}". '
                f'Only pending refunds can be processed.'
            )

        if action == 'approve':
            refund.status = 'approved'
            refund.admin_note = admin_note
            refund.processed_by = admin_user
            refund.save()

            # Notify the requester
            send_notification(
                user=refund.requested_by,
                title='Refund Approved',
                message=f'Your refund request for ${refund.amount:.2f} '
                        f'(Transaction: {refund.transaction.reference_number}) has been approved. '
                        f'The refund will be processed shortly.',
                notification_type='refund',
            )

        elif action == 'reject':
            refund.status = 'rejected'
            refund.admin_note = admin_note
            refund.processed_by = admin_user
            refund.save()

            # Notify the requester
            send_notification(
                user=refund.requested_by,
                title='Refund Rejected',
                message=f'Your refund request for ${refund.amount:.2f} '
                        f'(Transaction: {refund.transaction.reference_number}) has been rejected. '
                        f'Reason: {admin_note or "No reason provided"}',
                notification_type='refund',
            )

        return refund

    @staticmethod
    @db_transaction.atomic
    def complete_refund(refund, admin_user, admin_note=''):
        """
        Complete an approved refund. Returns money from receiver back to sender.
        Admin-only operation.

        Args:
            refund: The Refund instance to complete
            admin_user: The admin completing the refund
            admin_note: Optional admin note

        Returns:
            The updated Refund instance

        Raises:
            RefundError: If the refund cannot be completed
        """
        if refund.status != 'approved':
            raise RefundError(
                f'Cannot complete a refund with status "{refund.status}". '
                f'Only approved refunds can be completed.'
            )

        try:
            # Process the actual money transfer using TransactionService
            refund_transaction = TransactionService.process_refund(
                transaction=refund.transaction,
                refund_amount=refund.amount,
            )

            # Update refund status
            refund.status = 'completed'
            refund.admin_note = admin_note or refund.admin_note
            refund.processed_by = admin_user
            refund.save()

            # Notify the requester
            send_notification(
                user=refund.requested_by,
                title='Refund Completed',
                message=f'Your refund of ${refund.amount:.2f} '
                        f'(Transaction: {refund.transaction.reference_number}) has been completed. '
                        f'The money has been returned to your wallet.',
                notification_type='refund',
            )

            # Notify the other party
            other_user = refund.transaction.receiver_wallet.user
            if other_user != refund.requested_by:
                send_notification(
                    user=other_user,
                    title='Refund Processed',
                    message=f'A refund of ${refund.amount:.2f} has been processed for '
                            f'transaction {refund.transaction.reference_number}. '
                            f'The amount has been deducted from your wallet.',
                    notification_type='refund',
                )

            return refund

        except Exception as e:
            raise RefundError(f'Failed to complete refund: {str(e)}')
