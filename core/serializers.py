from rest_framework import serializers
from .models import Page, AdminUser
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db.models import Q

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # The 'username' field in attrs can be either email or username
        login_input = attrs.get("username")
        password = attrs.get("password")

        if login_input and password:
            # Check if input is email or username
            user_obj = AdminUser.objects.filter(
                Q(username=login_input) | Q(email=login_input)
            ).first()

            if user_obj:
                # If we found a user, set the username to the actual username
                # so the parent class can handle authentication
                attrs["username"] = user_obj.username
            
        data = super().validate(attrs)

        # Get the user object
        user = AdminUser.objects.get(username=self.user.username)
        
        # Serialize user data
        user_serializer = AdminUserSerializer(user)
        
        # Custom response format to match frontend expectations
        return {
            'user': user_serializer.data,
            'token': data['access'],
            'refreshToken': data['refresh']
        }


class PageRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ['email', 'prompt', 'page_type', 'theme']

    def validate_prompt(self, value):
        dangerous_patterns = ['<script', 'javascript:', 'onerror=']
        if any(pattern in value.lower() for pattern in dangerous_patterns):
            raise serializers.ValidationError("Invalid prompt content")
        return value


class PageResponseSerializer(serializers.ModelSerializer):
    live_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Page
        fields = ['id', 'live_url', 'created_at', 'page_type', 'theme', 'view_count', 'prompt', 'email']

    def get_live_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/p/{obj.id}/')
        return f'/p/{obj.id}/'


class AdminUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    name = serializers.CharField(source='first_name', required=False)
    
    class Meta:
        model = AdminUser
        fields = ['id', 'username', 'email', 'role', 'password', 'created_at', 'name']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        user = AdminUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', 'admin'),
            first_name=validated_data.get('first_name', '')
        )
        return user


class AdminDashboardStatsSerializer(serializers.Serializer):
    totalPages = serializers.IntegerField()
    pagesToday = serializers.IntegerField()
    totalViews = serializers.IntegerField()
    uniqueUsers = serializers.IntegerField()
