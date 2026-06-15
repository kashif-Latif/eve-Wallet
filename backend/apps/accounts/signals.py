from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from apps.wallets.models import Wallet
from apps.wallets.services import WalletService
from core.utils import generate_wallet_number

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    """
    Signal to auto-create a wallet when a new user is registered.
    The wallet is created with $1000 initial balance.
    """
    if created:
        # Only create wallet if it doesn't already exist
        if not hasattr(instance, 'wallet_id') or instance.wallet_id is None:
            try:
                wallet = Wallet.objects.create(
                    user=instance,
                    balance=1000.00,
                )
                # Update the user's wallet_id field
                User.objects.filter(pk=instance.pk).update(wallet_id=wallet)
            except Exception:
                # If wallet creation fails, try without the FK update
                try:
                    Wallet.objects.create(
                        user=instance,
                        balance=1000.00,
                    )
                except Exception:
                    pass


@receiver(post_save, sender=User)
def send_welcome_notification(sender, instance, created, **kwargs):
    """
    Signal to send a welcome notification to new users.
    """
    if created:
        from core.utils import send_notification
        send_notification(
            user=instance,
            title='Welcome to Digital Wallet!',
            message=f'Welcome {instance.first_name or instance.username}! '
                    f'Your digital wallet has been set up with $1,000.00 initial balance. '
                    f'Start sending and receiving money today!',
            notification_type='system',
        )
