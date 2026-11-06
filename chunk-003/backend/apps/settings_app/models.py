from django.db import models
from apps.core.models import TimeStampedModel

class StoreSettings(TimeStampedModel):
    store_name = models.CharField(max_length=200, default="فروشگاه")
    logo = models.ImageField(upload_to="settings/", blank=True, null=True)
    currency = models.CharField(max_length=10, default="IRT")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    invoice_prefix = models.CharField(max_length=20, default="INV")
    backup_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    email_enabled = models.BooleanField(default=False)
    branch_name = models.CharField(max_length=200, default="شعبه مرکزی - صندوق ۱", verbose_name="نام شعبه")
    support_phone = models.CharField(max_length=30, default="۰۲۱-۸۸۹۹۰۰۰۰", verbose_name="تلفن پشتیبانی")
    system_version = models.CharField(max_length=30, default="۴.۸.۲ سازمانی", verbose_name="نسخه سامانه")
