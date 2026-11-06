from django.db import models
from apps.core.models import TimeStampedModel

class Customer(TimeStampedModel):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True, db_index=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    credit_limit = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    loyalty_points = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class CustomerPayment(TimeStampedModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    method = models.CharField(max_length=50)
    reference = models.CharField(max_length=100, blank=True)
    note = models.TextField(blank=True)
    created_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True)
