from django.db import models
from django.conf import settings


class Refund(models.Model):
    """
    Refund model for the Digital Wallet System.
    Tracks refund requests, approval/rejection, and completion.
    """

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )

    transaction = models.ForeignKey(
        'transactions.Transaction',
        on_delete=models.CASCADE,
        related_name='refunds',
        help_text="The original transaction to be refunded"
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='refund_requests',
        help_text="The user who requested the refund"
    )
    reason = models.TextField(
        help_text="Reason for the refund request"
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
        help_text="Current status of the refund"
    )
    admin_note = models.TextField(
        blank=True,
        null=True,
        help_text="Admin note about the refund decision"
    )
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_refunds',
        help_text="Admin who processed the refund"
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Amount to be refunded"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = 'refunds'
        verbose_name = 'Refund'
        verbose_name_plural = 'Refunds'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['requested_by', '-created_at']),
            models.Index(fields=['transaction']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Refund for TXN {self.transaction.reference_number} - ${self.amount} - {self.get_status_display()}"
