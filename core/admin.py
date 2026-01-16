from django.contrib import admin
from .models import Page, AdminUser

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'page_type', 'theme', 'view_count', 'created_at']
    list_filter = ['page_type', 'theme', 'is_public', 'created_at']
    search_fields = ['email', 'prompt']
    readonly_fields = ['id', 'created_at', 'view_count']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('id', 'email', 'prompt')
        }),
        ('Page Details', {
            'fields': ('page_type', 'theme', 'html_content')
        }),
        ('Metadata', {
            'fields': ('view_count', 'is_public', 'meta_data', 'created_at', 'deleted_at')
        }),
    )

@admin.register(AdminUser)
class AdminUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['username', 'email']
