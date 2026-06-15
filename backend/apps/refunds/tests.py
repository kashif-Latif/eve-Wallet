from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal

from apps.accounts.models import User
from apps.wallets.models import Wallet
from apps.transactions.models import Transaction
from apps.transactions.services import TransactionService
from .models import Refund
from .services import RefundService


class RefundModelTest(TestCase):
    """Tests for the Refund model."""

    def setUp(self):
        self.sender = User.objects.create_user(
            username='refundsender',
            email='refundsender@example.com',
            phone='+7777777777',
            password='Test@123456',
            first_name='RefundSender',
            last_name='User',
        )
        self.sender.refresh_from_db()

        self.receiver = User.objects.create_user(
            username='refundreceiver',
            email='refundreceiver@example.com',
            phone='+8888888888',
            password='Test@123456',
            first_name='RefundReceiver',
            last_name='User',
        )
        self.receiver.refresh_from_db()

        self.transaction = TransactionService.send_money(
            sender_wallet=self.sender.wallet_id,
            receiver_wallet=self.receiver.wallet_id,
            amount=Decimal('100.00'),
        )

    def test_refund_creation(self):
        refund = Refund.objects.create(
            transaction=self.transaction,
            requested_by=self.sender,
            reason='Test refund reason',
            amount=Decimal('100.00'),
        )
        self.assertEqual(refund.status, 'pending')
        self.assertEqual(refund.amount, Decimal('100.00'))

    def test_refund_str(self):
        refund = Refund.objects.create(
            transaction=self.transaction,
            requested_by=self.sender,
            reason='Test refund reason',
            amount=Decimal('100.00'),
        )
        self.assertIn('TXN', str(refund))


class RefundServiceTest(TestCase):
    """Tests for the RefundService."""

    def setUp(self):
        self.sender = User.objects.create_user(
            username='refsvcsender',
            email='refsvcsender@example.com',
            phone='+9999999999',
            password='Test@123456',
            first_name='RefSvcSender',
            last_name='User',
        )
        self.sender.refresh_from_db()

        self.receiver = User.objects.create_user(
            username='refsvcreceiver',
            email='refsvcreceiver@example.com',
            phone='+1010101010',
            password='Test@123456',
            first_name='RefSvcReceiver',
            last_name='User',
        )
        self.receiver.refresh_from_db()

        self.admin = User.objects.create_user(
            username='refundadmin',
            email='refundadmin@example.com',
            phone='+1212121212',
            password='Test@123456',
            first_name='RefundAdmin',
            last_name='User',
            role='admin',
        )

        self.transaction = TransactionService.send_money(
            sender_wallet=self.sender.wallet_id,
            receiver_wallet=self.receiver.wallet_id,
            amount=Decimal('100.00'),
        )

    def test_request_refund(self):
        refund = RefundService.request_refund(
            user=self.sender,
            transaction=self.transaction,
            reason='Item not received',
        )
        self.assertEqual(refund.status, 'pending')
        self.assertEqual(refund.amount, Decimal('100.00'))

    def test_approve_refund(self):
        refund = RefundService.request_refund(
            user=self.sender,
            transaction=self.transaction,
            reason='Item not received',
        )
        updated = RefundService.process_refund(
            refund=refund,
            admin_user=self.admin,
            action='approve',
            admin_note='Approved',
        )
        self.assertEqual(updated.status, 'approved')

    def test_reject_refund(self):
        refund = RefundService.request_refund(
            user=self.sender,
            transaction=self.transaction,
            reason='Item not received',
        )
        updated = RefundService.process_refund(
            refund=refund,
            admin_user=self.admin,
            action='reject',
            admin_note='Not eligible',
        )
        self.assertEqual(updated.status, 'rejected')


class RefundAPITest(APITestCase):
    """Tests for the Refund API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.sender = User.objects.create_user(
            username='apirefundsender',
            email='apirefundsender@example.com',
            phone='+1313131313',
            password='Test@123456',
            first_name='ApiRefundSender',
            last_name='User',
        )
        self.sender.refresh_from_db()

        self.receiver = User.objects.create_user(
            username='apirefundreceiver',
            email='apirefundreceiver@example.com',
            phone='+1414141414',
            password='Test@123456',
            first_name='ApiRefundReceiver',
            last_name='User',
        )
        self.receiver.refresh_from_db()

        self.transaction = TransactionService.send_money(
            sender_wallet=self.sender.wallet_id,
            receiver_wallet=self.receiver.wallet_id,
            amount=Decimal('100.00'),
        )

    def test_request_refund_api(self):
        self.client.force_authenticate(user=self.sender)
        response = self.client.post('/api/refunds/request/', {
            'transaction_id': self.transaction.id,
            'reason': 'Test refund reason for API test',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_my_refunds_api(self):
        self.client.force_authenticate(user=self.sender)
        response = self.client.get('/api/refunds/my-refunds/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_refund_request(self):
        response = self.client.post('/api/refunds/request/', {
            'transaction_id': self.transaction.id,
            'reason': 'Unauthorized refund',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
