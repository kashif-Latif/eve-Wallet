from django.db import models
from django.conf import settings


class Notification(models.Model):
    """
    Notification model for the Digital Wallet System.
    Stores in-app notifications for users about transactions, refunds,
    system events, security alerts, and promotional messages.
    """

    NOTIFICATION_TYPE_CHOICES = (
        ('transaction', 'Transaction'),
        ('refund', 'Refund'),
        ('system', 'System'),
        ('security', 'Security'),
        ('promotional', 'Promotional'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text="The user who receives the notification"
    )
    title = models.CharField(
        max_length=200,
        help_text="Notification title"
    )
    message = models.TextField(
        help_text="Notification message body"
    )
    notification_type = models.CharField(
        max_length=15,
        choices=NOTIFICATION_TYPE_CHOICES,
        default='system',
        db_index=True,
        help_text="Type of notification"
    )
    is_read = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether the user has read the notification"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read', '-created_at']),
            models.Index(fields=['notification_type', '-created_at']),
        ]

    def __str__(self):
        return f"{self.notification_type}: {self.title} - {self.user.username}"
