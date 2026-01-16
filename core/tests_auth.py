from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import AdminUser

class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('admin-register')
        self.login_url = reverse('admin-login')
        self.user_data = {
            'username': 'testadmin',
            'name': 'Test Admin',
            'email': 'admin@test.com',
            'password': 'password123',
            'confirmPassword': 'password123'
        }

    def test_register_with_username(self):
        """
        Verify that we can register with a username.
        """
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(AdminUser.objects.filter(username='testadmin').exists())
        self.assertTrue(AdminUser.objects.filter(email='admin@test.com').exists())

    def test_login_with_username(self):
        """
        Verify login with username.
        """
        # Register first
        AdminUser.objects.create_user(
            username='testadmin',
            email='admin@test.com',
            password='password123'
        )

        login_data = {
            'username': 'testadmin',
            'password': 'password123'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_with_email(self):
        """
        Verify login with email.
        """
        # Register first
        AdminUser.objects.create_user(
            username='testadmin',
            email='admin@test.com',
            password='password123'
        )

        login_data = {
            'username': 'admin@test.com',  # The field is still named 'username' in the serializer input
            'password': 'password123'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_login_fail(self):
        """Verify login failure"""
        login_data = {
            'username': 'wrong',
            'password': 'password123'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
