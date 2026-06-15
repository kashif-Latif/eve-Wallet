from django.db import models
from django.conf import settings

from core.utils import generate_reference_number


class Transaction(models.Model):
    """
    Transaction model for the Digital Wallet System.
    Records all money transfers, deposits, withdrawals, and refunds.
    Uses transaction.atomic() for all money transfers with rollback on failure.
    """

    TRANSACTION_TYPE_CHOICES = (
        ('transfer', 'Transfer'),
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('refund', 'Refund'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )

    sender_wallet = models.ForeignKey(
        'wallets.Wallet',
        on_delete=models.CASCADE,
        related_name='sent_transactions',
        help_text="The wallet sending the money"
    )
    receiver_wallet = models.ForeignKey(
        'wallets.Wallet',
        on_delete=models.CASCADE,
        related_name='received_transactions',
        help_text="The wallet receiving the money"
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Transaction amount"
    )
    fee = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Transaction fee"
    )
    transaction_type = models.CharField(
        max_length=15,
        choices=TRANSACTION_TYPE_CHOICES,
        db_index=True,
        help_text="Type of transaction"
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
        help_text="Current status of the transaction"
    )
    reference_number = models.CharField(
        max_length=15,
        unique=True,
        default=generate_reference_number,
        db_index=True,
        help_text="Unique reference number (TXN + 12 chars)"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Transaction description or note"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = 'transactions'
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['reference_number']),
            models.Index(fields=['transaction_type', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['sender_wallet', '-created_at']),
            models.Index(fields=['receiver_wallet', '-created_at']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"TXN {self.reference_number} - {self.get_transaction_type_display()} - ${self.amount}"

    @property
    def total_amount(self):
        """Total amount including fee."""
        return self.amount + self.fee
