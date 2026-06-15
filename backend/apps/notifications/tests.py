from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from apps.accounts.models import User
from .models import Notification
from core.utils import send_notification


class NotificationModelTest(TestCase):
    """Tests for the Notification model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='notifuser',
            email='notif@example.com',
            phone='+1515151515',
            password='Test@123456',
            first_name='Notif',
            last_name='User',
        )

    def test_notification_creation(self):
        notif = Notification.objects.create(
            user=self.user,
            title='Test Notification',
            message='This is a test notification',
            notification_type='system',
        )
        self.assertEqual(notif.title, 'Test Notification')
        self.assertFalse(notif.is_read)
        self.assertEqual(notif.notification_type, 'system')

    def test_notification_str(self):
        notif = Notification.objects.create(
            user=self.user,
            title='Test',
            message='Test message',
            notification_type='transaction',
        )
        self.assertIn('transaction', str(notif).lower())


class SendNotificationUtilTest(TestCase):
    """Tests for the send_notification utility function."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='notifutiluser',
            email='notifutil@example.com',
            phone='+1616161616',
            password='Test@123456',
            first_name='NotifUtil',
            last_name='User',
        )

    def test_send_notification(self):
        notif = send_notification(
            user=self.user,
            title='Test',
            message='Test message',
            notification_type='system',
        )
        self.assertIsNotNone(notif)
        self.assertEqual(notif.title, 'Test')
        self.assertEqual(notif.notification_type, 'system')

    def test_send_notification_invalid_type(self):
        notif = send_notification(
            user=self.user,
            title='Test',
            message='Test message',
            notification_type='invalid_type',
        )
        # Should default to 'system' type
        self.assertEqual(notif.notification_type, 'system')


class NotificationAPITest(APITestCase):
    """Tests for the Notification API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='notifapiuser',
            email='notifapi@example.com',
            phone='+1717171717',
            password='Test@123456',
            first_name='NotifApi',
            last_name='User',
        )

        # Create some notifications
        for i in range(5):
            Notification.objects.create(
                user=self.user,
                title=f'Notification {i+1}',
                message=f'Test message {i+1}',
                notification_type='system' if i % 2 == 0 else 'transaction',
                is_read=i < 2,  # First 2 are read
            )

    def test_list_notifications(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_mark_notification_read(self):
        self.client.force_authenticate(user=self.user)
        unread_notif = Notification.objects.filter(user=self.user, is_read=False).first()
        response = self.client.put(f'/api/notifications/{unread_notif.id}/read/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        unread_notif.refresh_from_db()
        self.assertTrue(unread_notif.is_read)

    def test_mark_all_read(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.put('/api/notifications/read-all/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        unread_count = Notification.objects.filter(user=self.user, is_read=False).count()
        self.assertEqual(unread_count, 0)

    def test_unread_count(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/notifications/unread-count/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['unread_count'], 3)
