from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import User


class UserModelTest(TestCase):
    """Tests for the custom User model."""

    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'phone': '+1234567890',
            'password': 'Test@123456',
            'first_name': 'Test',
            'last_name': 'User',
        }

    def test_create_user(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.phone, '+1234567890')
        self.assertEqual(user.role, 'user')
        self.assertFalse(user.is_verified)

    def test_user_str(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), 'testuser (+1234567890)')

    def test_user_full_name(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.full_name, 'Test User')

    def test_is_admin_property(self):
        user = User.objects.create_user(**self.user_data)
        self.assertFalse(user.is_admin)
        user.role = 'admin'
        user.save()
        self.assertTrue(user.is_admin)

    def test_wallet_auto_created(self):
        user = User.objects.create_user(**self.user_data)
        user.refresh_from_db()
        self.assertIsNotNone(user.wallet_id)
        self.assertEqual(user.wallet_id.balance, 1000.00)


class AuthAPITest(APITestCase):
    """Tests for authentication API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('accounts:register')
        self.login_url = reverse('accounts:login')
        self.profile_url = reverse('accounts:profile')
        self.change_password_url = reverse('accounts:change_password')

        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'phone': '+1234567890',
            'password': 'Test@123456',
            'confirm_password': 'Test@123456',
            'first_name': 'Test',
            'last_name': 'User',
        }

    def test_user_registration(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)

    def test_user_registration_password_mismatch(self):
        data = self.user_data.copy()
        data['confirm_password'] = 'WrongPassword@123'
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login(self):
        # Register user first
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            phone='+1234567890',
            password='Test@123456',
            first_name='Test',
            last_name='User',
        )

        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'Test@123456',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_login_invalid_credentials(self):
        response = self.client.post(self.login_url, {
            'username': 'nonexistent',
            'password': 'wrongpassword',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            phone='+1234567890',
            password='Test@123456',
            first_name='Test',
            last_name='User',
        )
        self.client.force_authenticate(user=user)

        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

    def test_unauthenticated_profile_access(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
