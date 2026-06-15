from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    """
    Custom user model extending AbstractUser for the Digital Wallet System.
    Includes phone number, role-based access, and profile information.
    """

    ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
        ('superadmin', 'Super Admin'),
    )

    phone_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )

    phone = models.CharField(
        max_length=17,
        unique=True,
        validators=[phone_validator],
        help_text="Phone number in international format"
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='user',
        db_index=True
    )
    is_verified = models.BooleanField(
        default=False,
        help_text="Whether the user has verified their phone/email"
    )
    profile_picture = models.ImageField(
        upload_to='profile_pictures/%Y/%m/',
        blank=True,
        null=True,
        help_text="User profile picture"
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        help_text="User date of birth"
    )
    address = models.TextField(
        blank=True,
        null=True,
        help_text="User street address"
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="User city"
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="User country"
    )
    transaction_pin = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        help_text="Hashed 4-digit PIN for transaction confirmation"
    )
    pin_set = models.BooleanField(
        default=False,
        help_text="Whether the user has set their transaction PIN"
    )
    wallet_id = models.ForeignKey(
        'wallets.Wallet',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_wallet',
        help_text="Auto-created wallet for this user"
    )

    # Override email to be unique and required
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'phone']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['phone']),
            models.Index(fields=['role']),
            models.Index(fields=['is_verified']),
        ]

    def __str__(self):
        return f"{self.username} ({self.phone})"

    @property
    def is_admin(self):
        return self.role in ('admin', 'superadmin')

    @property
    def is_superadmin(self):
        return self.role == 'superadmin'

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class AuditLog(models.Model):
    """
    Audit log model to track all significant actions in the system.
    Automatically populated by AuditLogMiddleware.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        help_text="The user who performed the action"
    )
    action = models.CharField(
        max_length=20,
        help_text="Type of action: READ, CREATE, UPDATE, DELETE"
    )
    model_name = models.CharField(
        max_length=100,
        help_text="Name of the model affected"
    )
    object_id = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="ID of the affected object"
    )
    changes = models.JSONField(
        default=dict,
        blank=True,
        help_text="Details of the changes made"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the request"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        db_table = 'audit_logs'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['model_name', '-created_at']),
            models.Index(fields=['action', '-created_at']),
        ]

    def __str__(self):
        return f"{self.action} on {self.model_name} by {self.user or 'Anonymous'}"
