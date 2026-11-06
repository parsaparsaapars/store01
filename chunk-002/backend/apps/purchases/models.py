from django.db import models
from apps.core.models import TimeStampedModel

class Supplier(TimeStampedModel):
    company_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.company_name

class PurchaseOrder(TimeStampedModel):
    STATUS = [("draft","draft"),("pending","pending"),("approved","approved"),("received","received"),("cancelled","cancelled")]
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="orders")
    warehouse = models.ForeignKey("inventory.Warehouse", on_delete=models.PROTECT)
    order_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="draft")
    discount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    shipping = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    note = models.TextField(blank=True)
    created_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True)

class PurchaseItem(TimeStampedModel):
    order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("products.Product", on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=18, decimal_places=3)
    unit_price = models.DecimalField(max_digits=18, decimal_places=2)
    discount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=18, decimal_places=2, default=0)

class PurchaseReceipt(TimeStampedModel):
    order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="receipts")
    receipt_date = models.DateField()
    note = models.TextField(blank=True)
    created_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True)
