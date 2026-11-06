from django.db import models
from apps.core.models import TimeStampedModel

class Notification(TimeStampedModel):
    PRIORITY = [("low","low"),("normal","normal"),("high","high"),("critical","critical")]
    title = models.CharField(max_length=200)
    message = models.TextField()
    category = models.CharField(max_length=100)
    priority = models.CharField(max_length=20, choices=PRIORITY, default="normal")
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=200, blank=True)
    user = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True)
