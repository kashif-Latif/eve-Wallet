from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal

from apps.accounts.models import User
from .models import Wallet
from .services import WalletService


class WalletModelTest(TestCase):
    """Tests for the Wallet model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='walletuser',
            email='wallet@example.com',
            phone='+1111111111',
            password='Test@123456',
            first_name='Wallet',
            last_name='User',
        )
        self.user.refresh_from_db()

    def test_wallet_auto_created(self):
        """Test that wallet is auto-created on user registration."""
        self.assertIsNotNone(self.user.wallet_id)
        wallet = self.user.wallet_id
        self.assertEqual(wallet.balance, Decimal('1000.00'))
        self.assertTrue(wallet.is_active)
        self.assertFalse(wallet.is_frozen)

    def test_wallet_number_unique(self):
        """Test that wallet numbers are unique."""
        wallet1 = self.user.wallet_id
        user2 = User.objects.create_user(
            username='walletuser2',
            email='wallet2@example.com',
            phone='+2222222222',
            password='Test@123456',
            first_name='Wallet2',
            last_name='User2',
        )
        user2.refresh_from_db()
        wallet2 = user2.wallet_id
        self.assertNotEqual(wallet1.wallet_number, wallet2.wallet_number)

    def test_wallet_can_transact(self):
        """Test wallet can_transact method."""
        wallet = self.user.wallet_id
        self.assertTrue(wallet.can_transact())

        wallet.is_frozen = True
        wallet.save()
        self.assertFalse(wallet.can_transact())

    def test_wallet_available_balance(self):
        """Test available_balance property."""
        wallet = self.user.wallet_id
        self.assertEqual(wallet.available_balance, Decimal('1000.00'))

        wallet.is_frozen = True
        wallet.save()
        self.assertEqual(wallet.available_balance, 0)


class WalletServiceTest(TestCase):
    """Tests for the WalletService."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='serviceuser',
            email='service@example.com',
            phone='+3333333333',
            password='Test@123456',
            first_name='Service',
            last_name='User',
        )
        self.user.refresh_from_db()
        self.wallet = self.user.wallet_id

    def test_deposit(self):
        """Test wallet deposit."""
        WalletService.deposit(self.wallet, Decimal('500.00'))
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('1500.00'))

    def test_withdraw(self):
        """Test wallet withdrawal."""
        WalletService.withdraw(self.wallet, Decimal('200.00'))
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('800.00'))

    def test_withdraw_insufficient_funds(self):
        """Test withdrawal with insufficient funds."""
        from core.utils import InsufficientFundsError
        with self.assertRaises(InsufficientFundsError):
            WalletService.withdraw(self.wallet, Decimal('2000.00'))

    def test_freeze_wallet(self):
        """Test freezing a wallet."""
        admin = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            phone='+4444444444',
            password='Test@123456',
            first_name='Admin',
            last_name='User',
            role='admin',
        )
        WalletService.freeze_wallet(self.wallet, admin, 'Suspicious activity')
        self.wallet.refresh_from_db()
        self.assertTrue(self.wallet.is_frozen)

    def test_unfreeze_wallet(self):
        """Test unfreezing a wallet."""
        admin = User.objects.create_user(
            username='adminuser2',
            email='admin2@example.com',
            phone='+5555555555',
            password='Test@123456',
            first_name='Admin2',
            last_name='User2',
            role='admin',
        )
        self.wallet.is_frozen = True
        self.wallet.save()

        WalletService.unfreeze_wallet(self.wallet, admin, 'Issue resolved')
        self.wallet.refresh_from_db()
        self.assertFalse(self.wallet.is_frozen)


class WalletAPITest(APITestCase):
    """Tests for the Wallet API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='apiuser',
            email='api@example.com',
            phone='+6666666666',
            password='Test@123456',
            first_name='API',
            last_name='User',
        )
        self.user.refresh_from_db()
        self.wallet = self.user.wallet_id

    def test_get_my_wallet(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/wallets/my-wallet/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

    def test_get_balance(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/wallets/balance/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['balance'], '1000.00')

    def test_unauthenticated_access(self):
        response = self.client.get('/api/wallets/my-wallet/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
