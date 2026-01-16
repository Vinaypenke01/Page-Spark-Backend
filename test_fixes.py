import os
import django
from django.test import RequestFactory
from rest_framework.test import force_authenticate

import sys
sys.path.append('d:\\livepage\\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.views import AdminMeView
from core.models import AdminUser, Page
from core.serializers import PageResponseSerializer

def test_admin_me_view():
    print("\n--- Testing AdminMeView ---")
    factory = RequestFactory()
    user = AdminUser.objects.create_user(username='test_me', email='test_me@example.com', password='password', first_name='Test Name')
    
    view = AdminMeView.as_view()
    request = factory.get('/api/admin/me/')
    force_authenticate(request, user=user)
    
    response = view(request)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Success! Data:", response.data)
        if response.data['user']['name'] == 'Test Name':
             print("Verified: Name field is present and correct.")
    else:
        print("Failed!")
    
    user.delete()

def test_page_serializer():
    print("\n--- Testing PageResponseSerializer ---")
    page = Page.objects.create(email='test@example.com', prompt='This is a test prompt longer than 10 chars', html_content='<html></html>')
    
    serializer = PageResponseSerializer(page)
    data = serializer.data
    print("Serialized Keys:", data.keys())
    
    required_fields = ['prompt', 'email', 'live_url']
    missing = [f for f in required_fields if f not in data]
    
    if not missing:
        print("Success! All required fields including 'prompt' and 'email' are present.")
    else:
        print(f"Failed! Missing fields: {missing}")
        
    page.delete()

if __name__ == '__main__':
    try:
        test_admin_me_view()
        test_page_serializer()
    except Exception as e:
        print(f"An error occurred: {e}")
