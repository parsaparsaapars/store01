from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from apps.core.models import TimeStampedModel

class Role(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    permissions = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name

class User(AbstractUser, TimeStampedModel):
    phone = models.CharField(max_length=20, blank=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name="users")
    branch = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.username

class AuditLog(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)
    module = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    before = models.JSONField(null=True, blank=True)
    after = models.JSONField(null=True, blank=True)
    result = models.CharField(max_length=50, default="success")

    class Meta:
        ordering = ["-created_at"]
