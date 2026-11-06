from django.db import models
from apps.core.models import TimeStampedModel
from apps.products.models import Product

class Warehouse(TimeStampedModel):
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    manager = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Stock(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stocks")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="stocks")
    quantity = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    reserved = models.DecimalField(max_digits=18, decimal_places=3, default=0)

    class Meta:
        unique_together = ("product", "warehouse")

    @property
    def available(self):
        return self.quantity - self.reserved

class StockMovement(TimeStampedModel):
    MOVEMENT_TYPES = [
        ("in","in"),("out","out"),("transfer","transfer"),
        ("adjustment","adjustment"),("return","return"),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.DecimalField(max_digits=18, decimal_places=3)
    reference = models.CharField(max_length=100, blank=True)
    note = models.TextField(blank=True)
    created_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True)

class StockTransfer(TimeStampedModel):
    STATUS = [("requested","requested"),("sent","sent"),("received","received"),("cancelled","cancelled")]
    from_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="transfers_out")
    to_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="transfers_in")
    transfer_date = models.DateField()
    document_no = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="requested")
    note = models.TextField(blank=True)

class StockTransferItem(TimeStampedModel):
    transfer = models.ForeignKey(StockTransfer, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=18, decimal_places=3)
