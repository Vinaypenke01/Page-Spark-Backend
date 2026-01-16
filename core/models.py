import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from django.utils import timezone

class AdminUser(AbstractUser):
    """
    Custom admin user model for the Page Spark system.
    """
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('super_admin', 'Super Admin'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='admin')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'admin_users'
        verbose_name = 'Admin User'
        verbose_name_plural = 'Admin Users'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class PageManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class Page(models.Model):
    PAGE_TYPE_CHOICES = [
        ('birthday', 'Birthday Invitation'),
        ('event', 'Event Page'),
        ('landing', 'Landing Page'),
        ('portfolio', 'Portfolio'),
        ('announcement', 'Announcement'),
        ('other', 'Other'),
    ]
    
    THEME_CHOICES = [
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('colorful', 'Colorful & Fun'),
        ('modern', 'Modern'),
        ('elegant', 'Elegant'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(db_index=True)
    prompt = models.TextField(
        validators=[MinLengthValidator(10)],
        help_text="Minimum 10 characters description"
    )
    page_type = models.CharField(
        max_length=50, 
        choices=PAGE_TYPE_CHOICES,
        default='other'
    )
    theme = models.CharField(
        max_length=50, 
        choices=THEME_CHOICES,
        default='modern'
    )
    html_content = models.TextField()
    is_public = models.BooleanField(default=True)
    view_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    meta_data = models.JSONField(default=dict, blank=True)
    
    # Soft delete
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Managers
    objects = models.Manager()  # The default manager
    active_objects = PageManager()  # Manager for non-deleted pages

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', '-created_at']),
            models.Index(fields=['created_at']),
        ]

    def delete(self, soft=True, *args, **kwargs):
        if soft:
            self.deleted_at = timezone.now()
            self.save()
        else:
            super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.get_page_type_display()} by {self.email} ({self.id})"

    def __repr__(self):
        return f"<Page id={self.id} email={self.email} type={self.page_type}>"
