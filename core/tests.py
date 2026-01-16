from django.test import TestCase, Client
from django.urls import reverse
from .models import Page, AdminUser
from .services import HtmlSanitizationService
import uuid

class ModelTests(TestCase):
    def test_page_creation(self):
        page = Page.objects.create(
            email="test@example.com",
            prompt="A very long test prompt for validation.",
            page_type="landing",
            theme="dark",
            html_content="<html></html>"
        )
        self.assertEqual(Page.objects.count(), 1)
        self.assertEqual(str(page), "Landing Page by test@example.com (" + str(page.id) + ")")

    def test_soft_delete(self):
        page = Page.objects.create(email="test@example.com", prompt="Valid prompt length here.")
        page.delete()
        self.assertIsNotNone(page.deleted_at)
        self.assertEqual(Page.objects.count(), 1)  # Still in DB
        self.assertEqual(Page.active_objects.count(), 0)  # But not active

class SanitizationTests(TestCase):
    def test_removes_script_tags(self):
        malicious_html = '<p>Hello</p><script>alert("XSS")</script>'
        clean = HtmlSanitizationService.sanitize(malicious_html)
        # It should remove the malicious script but add the Tailwind CDN script
        self.assertNotIn('alert("XSS")', clean)
        self.assertIn('https://cdn.tailwindcss.com', clean)
        # Should NOT have the original malicious script tag
        self.assertNotIn('alert(', clean)

    def test_preserves_tailwind(self):
        html = '<div class="bg-blue-500">Test</div>'
        clean = HtmlSanitizationService.sanitize(html)
        self.assertIn('class="bg-blue-500"', clean)
        self.assertIn('https://cdn.tailwindcss.com', clean)

class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = AdminUser.objects.create_user(
            username='admin', 
            email='admin@test.com', 
            password='Password123!',
            role='admin'
        )

    def test_generate_page_throttling(self):
        url = reverse('generate-page')
        data = {
            "email": "user@test.com",
            "prompt": "Generating a page for testing throttling.",
            "page_type": "landing",
            "theme": "dark"
        }
        # First request should be fine
        response = self.client.post(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_admin_dashboard_unauthorized(self):
        url = reverse('admin-dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_admin_login(self):
        url = reverse('admin-login')
        data = {
            "username": "admin",
            "password": "Password123!"
        }
        response = self.client.post(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
