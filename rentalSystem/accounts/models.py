from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class User(AbstractUser):
    """Custom user model to allow future extensions."""
    # Add future fields here (e.g., phone, avatar)
    pass


class StoreUser(models.Model):
    ROLE_OWNER = 'owner'
    ROLE_ADMIN = 'admin'
    ROLE_STAFF = 'staff'

    ROLE_CHOICES = [
        (ROLE_OWNER, 'Owner'),
        (ROLE_ADMIN, 'Admin'),
        (ROLE_STAFF, 'Staff'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='store_memberships')
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, related_name='members')
    role = models.CharField(max_length=16, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('user', 'store')]
        verbose_name = 'Store User'
        verbose_name_plural = 'Store Users'

    def __str__(self) -> str:
        return f"{self.user.username} @ {self.store.slug} ({self.role})"
