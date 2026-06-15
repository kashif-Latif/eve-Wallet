from django.db import models
from django.conf import settings

from core.utils import generate_wallet_number


class Wallet(models.Model):
    """
    Wallet model for the Digital Wallet System.
    Each user has exactly one wallet (OneToOne relationship via User.wallet_id).
    Auto-created with $1000 balance on user registration via signal.
    """

    CURRENCY_CHOICES = (
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('PKR', 'Pakistani Rupee'),
        ('INR', 'Indian Rupee'),
        ('SAR', 'Saudi Riyal'),
        ('AED', 'UAE Dirham'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet',
        help_text="The owner of this wallet"
    )
    wallet_number = models.CharField(
        max_length=12,
        unique=True,
        default=generate_wallet_number,
        db_index=True,
        help_text="Unique 12-digit wallet number"
    )
    balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=1000.00,
        help_text="Current wallet balance (starts at $1,000.00)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the wallet is active"
    )
    is_frozen = models.BooleanField(
        default=False,
        help_text="Whether the wallet is frozen (admin action)"
    )
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='USD',
        help_text="Wallet currency"
    )
    daily_limit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=10000.00,
        help_text="Maximum daily transaction amount"
    )
    monthly_limit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=100000.00,
        help_text="Maximum monthly transaction amount"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = 'wallets'
        verbose_name = 'Wallet'
        verbose_name_plural = 'Wallets'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['wallet_number']),
            models.Index(fields=['is_active', 'is_frozen']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"Wallet {self.wallet_number} - {self.user.username} (${self.balance})"

    @property
    def available_balance(self):
        """Return the balance available for spending (considering frozen status)."""
        if self.is_frozen or not self.is_active:
            return 0
        return self.balance

    def can_transact(self):
        """Check if the wallet can perform transactions."""
        return self.is_active and not self.is_frozen

    def has_sufficient_funds(self, amount):
        """Check if the wallet has sufficient funds for a given amount."""
        from decimal import Decimal
        return self.balance >= Decimal(str(amount))
