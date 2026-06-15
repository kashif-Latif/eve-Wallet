from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal

from apps.accounts.models import User
from apps.wallets.models import Wallet
from apps.transactions.services import TransactionService


class AnalyticsAPITest(APITestCase):
    """Tests for the Analytics API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='analyticsuser',
            email='analytics@example.com',
            phone='+1818181818',
            password='Test@123456',
            first_name='Analytics',
            last_name='User',
        )
        self.user.refresh_from_db()

        self.receiver = User.objects.create_user(
            username='analyticsreceiver',
            email='analyticsrecv@example.com',
            phone='+1919191919',
            password='Test@123456',
            first_name='AnalyticsRecv',
            last_name='User',
        )
        self.receiver.refresh_from_db()

        self.admin = User.objects.create_user(
            username='analyticsadmin',
            email='analyticsadmin@example.com',
            phone='+2020202020',
            password='Test@123456',
            first_name='AnalyticsAdmin',
            last_name='User',
            role='admin',
        )
        self.admin.refresh_from_db()

        # Create a transaction
        TransactionService.send_money(
            sender_wallet=self.user.wallet_id,
            receiver_wallet=self.receiver.wallet_id,
            amount=Decimal('50.00'),
        )

    def test_user_dashboard_stats(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/analytics/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('wallet_balance', response.data['data'])

    def test_transactions_chart(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/analytics/transactions-chart/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_dashboard_stats(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/analytics/admin/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_users', response.data['data'])

    def test_revenue_stats(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/analytics/revenue/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_revenue', response.data['data'])

    def test_non_admin_revenue_access(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/analytics/revenue/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_access(self):
        response = self.client.get('/api/analytics/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
