from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal

from apps.accounts.models import User
from apps.wallets.models import Wallet
from .models import Transaction
from .services import TransactionService


class TransactionModelTest(TestCase):
    """Tests for the Transaction model."""

    def setUp(self):
        self.sender = User.objects.create_user(
            username='sender',
            email='sender@example.com',
            phone='+1111111111',
            password='Test@123456',
            first_name='Sender',
            last_name='User',
        )
        self.sender.refresh_from_db()

        self.receiver = User.objects.create_user(
            username='receiver',
            email='receiver@example.com',
            phone='+2222222222',
            password='Test@123456',
            first_name='Receiver',
            last_name='User',
        )
        self.receiver.refresh_from_db()

    def test_transaction_creation(self):
        txn = Transaction.objects.create(
            sender_wallet=self.sender.wallet_id,
            receiver_wallet=self.receiver.wallet_id,
            amount=Decimal('100.00'),
            fee=Decimal('1.50'),
            transaction_type='transfer',
            status='completed',
        )
        self.assertEqual(txn.transaction_type, 'transfer')
        self.assertEqual(txn.status, 'completed')
        self.assertTrue(txn.reference_number.startswith('TXN'))

    def test_transaction_total_amount(self):
        txn = Transaction.objects.create(
            sender_wallet=self.sender.wallet_id,
            receiver_wallet=self.receiver.wallet_id,
            amount=Decimal('100.00'),
            fee=Decimal('1.50'),
            transaction_type='transfer',
            status='completed',
        )
        self.assertEqual(txn.total_amount, Decimal('101.50'))


class TransactionServiceTest(TestCase):
    """Tests for the TransactionService."""

    def setUp(self):
        self.sender = User.objects.create_user(
            username='txsender',
            email='txsender@example.com',
            phone='+3333333333',
            password='Test@123456',
            first_name='TxSender',
            last_name='User',
        )
        self.sender.refresh_from_db()

        self.receiver = User.objects.create_user(
            username='txreceiver',
            email='txreceiver@example.com',
            phone='+4444444444',
            password='Test@123456',
            first_name='TxReceiver',
            last_name='User',
        )
        self.receiver.refresh_from_db()

    def test_send_money(self):
        """Test successful money transfer."""
        txn = TransactionService.send_money(
            sender_wallet=self.sender.wallet_id,
            receiver_wallet=self.receiver.wallet_id,
            amount=Decimal('100.00'),
        )

        self.sender.wallet_id.refresh_from_db()
        self.receiver.wallet_id.refresh_from_db()

        self.assertEqual(txn.status, 'completed')
        self.assertEqual(txn.transaction_type, 'transfer')
        # Sender balance decreased (amount + fee)
        self.assertLess(self.sender.wallet_id.balance, Decimal('1000.00'))
        # Receiver balance increased
        self.assertEqual(self.receiver.wallet_id.balance, Decimal('1100.00'))

    def test_send_money_insufficient_funds(self):
        """Test transfer with insufficient funds."""
        from core.utils import InsufficientFundsError
        with self.assertRaises(InsufficientFundsError):
            TransactionService.send_money(
                sender_wallet=self.sender.wallet_id,
                receiver_wallet=self.receiver.wallet_id,
                amount=Decimal('2000.00'),
            )

    def test_deposit(self):
        """Test wallet deposit."""
        txn = TransactionService.deposit(
            wallet=self.sender.wallet_id,
            amount=Decimal('500.00'),
        )

        self.sender.wallet_id.refresh_from_db()
        self.assertEqual(txn.status, 'completed')
        self.assertEqual(txn.transaction_type, 'deposit')
        self.assertEqual(self.sender.wallet_id.balance, Decimal('1500.00'))

    def test_withdraw(self):
        """Test wallet withdrawal."""
        txn = TransactionService.withdraw(
            wallet=self.sender.wallet_id,
            amount=Decimal('200.00'),
        )

        self.sender.wallet_id.refresh_from_db()
        self.assertEqual(txn.status, 'completed')
        self.assertEqual(txn.transaction_type, 'withdrawal')
        self.assertLess(self.sender.wallet_id.balance, Decimal('1000.00'))


class TransactionAPITest(APITestCase):
    """Tests for the Transaction API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.sender = User.objects.create_user(
            username='apisender',
            email='apisender@example.com',
            phone='+5555555555',
            password='Test@123456',
            first_name='ApiSender',
            last_name='User',
        )
        self.sender.refresh_from_db()

        self.receiver = User.objects.create_user(
            username='apireceiver',
            email='apireceiver@example.com',
            phone='+6666666666',
            password='Test@123456',
            first_name='ApiReceiver',
            last_name='User',
        )
        self.receiver.refresh_from_db()

    def test_send_money_api(self):
        self.client.force_authenticate(user=self.sender)
        response = self.client.post('/api/transactions/send/', {
            'receiver_wallet_number': self.receiver.wallet_id.wallet_number,
            'amount': '100.00',
            'description': 'Test transfer',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])

    def test_deposit_api(self):
        self.client.force_authenticate(user=self.sender)
        response = self.client.post('/api/transactions/deposit/', {
            'amount': '500.00',
            'description': 'Test deposit',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_transaction_list_api(self):
        self.client.force_authenticate(user=self.sender)
        response = self.client.get('/api/transactions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_send_money(self):
        response = self.client.post('/api/transactions/send/', {
            'receiver_wallet_number': self.receiver.wallet_id.wallet_number,
            'amount': '100.00',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
