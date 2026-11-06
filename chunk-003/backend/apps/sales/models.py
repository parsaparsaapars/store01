from django.db import models
from apps.core.models import TimeStampedModel
from apps.customers.models import Customer

class Invoice(TimeStampedModel):
    STATUS = [("draft","draft"),("final","final"),("cancelled","cancelled")]
    PAYMENT_STATUS = [("unpaid","unpaid"),("partial","partial"),("paid","paid")]
    invoice_no = models.CharField(max_length=100, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    invoice_date = models.DateField()
    warehouse = models.ForeignKey("inventory.Warehouse", on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS, default="draft")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default="unpaid")
    subtotal = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    discount_mode = models.CharField(max_length=10, choices=[("amount", "amount"), ("percent", "percent")], default="amount")
    discount_input = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    tax = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    tax_mode = models.CharField(max_length=10, choices=[("amount", "amount"), ("percent", "percent")], default="amount")
    tax_input = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    shipping = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    note = models.TextField(blank=True)
    created_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True)

class InvoiceItem(TimeStampedModel):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("products.Product", on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=18, decimal_places=3)
    unit_price = models.DecimalField(max_digits=18, decimal_places=2)
    discount = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=18, decimal_places=2, default=0)

class InvoicePayment(TimeStampedModel):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    method = models.CharField(max_length=50)
    reference = models.CharField(max_length=100, blank=True)

class SalesReturn(TimeStampedModel):
    STATUS = [("requested","requested"),("approved","approved"),("completed","completed"),("cancelled","cancelled")]
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name="returns")
    return_date = models.DateField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="requested")
    refund_method = models.CharField(max_length=50, blank=True)
    total = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    created_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True)

class SalesReturnItem(TimeStampedModel):
    sales_return = models.ForeignKey(SalesReturn, on_delete=models.CASCADE, related_name="items")
    invoice_item = models.ForeignKey(InvoiceItem, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=18, decimal_places=3)
    condition = models.CharField(max_length=50, blank=True)
