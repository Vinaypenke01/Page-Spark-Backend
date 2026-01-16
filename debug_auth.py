import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.serializers import CustomTokenObtainPairSerializer
from core.models import AdminUser

# Cleanup
AdminUser.objects.filter(username='testdebug').delete()

# Create user
user = AdminUser.objects.create_user(username='testdebug', email='debug@test.com', password='password123')
print(f"Created user: {user.username} / {user.email}")

# Test Login with Email
print("\n--- Testing Login with Email ---")
data = {'username': 'debug@test.com', 'password': 'password123'}
serializer = CustomTokenObtainPairSerializer(data=data)
if serializer.is_valid():
    print("SUCCESS: Serializer is valid")
    print("User in validated_data:", serializer.validated_data.get('user'))
else:
    print("FAILURE: Serializer is invalid")
    print(serializer.errors)

# Test Login with Username
print("\n--- Testing Login with Username ---")
data = {'username': 'testdebug', 'password': 'password123'}
serializer2 = CustomTokenObtainPairSerializer(data=data)
if serializer2.is_valid():
    print("SUCCESS: Serializer is valid")
else:
    print("FAILURE: Serializer is invalid")
    print(serializer2.errors)

# Cleanup
user.delete()
