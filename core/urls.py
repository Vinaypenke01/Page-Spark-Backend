from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    GeneratePageView, 
    UserHistoryView, 
    AdminDashboardView, 
    AdminRegisterView,
    CustomTokenObtainPairView,
    AdminMeView,
    GeneratePromptView
)

urlpatterns = [
    # Public API
    path('api/generate/', GeneratePageView.as_view(), name='generate-page'),
    path('api/generate-prompt/', GeneratePromptView.as_view(), name='generate-prompt'),
    path('api/history/', UserHistoryView.as_view(), name='user-history'),
    
    # Auth API
    path('api/auth/register/', AdminRegisterView.as_view(), name='admin-register'),
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='admin-login'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # Admin API
    path('api/admin/dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    path('api/admin/me/', AdminMeView.as_view(), name='admin-me'),
]
