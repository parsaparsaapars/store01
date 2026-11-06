from django.db import models
from apps.core.models import TimeStampedModel

class Category(TimeStampedModel):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="children")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Brand(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Unit(TimeStampedModel):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Product(TimeStampedModel):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=100, unique=True)
    barcode = models.CharField(max_length=100, blank=True, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True)
    cost_price = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    sale_price = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    min_stock = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class PriceList(TimeStampedModel):
    name = models.CharField(max_length=100)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="prices")
    price = models.DecimalField(max_digits=18, decimal_places=2)
    valid_from = models.DateField(null=True, blank=True)
    valid_to = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

class Discount(TimeStampedModel):
    name = models.CharField(max_length=100)
    discount_type = models.CharField(max_length=20, choices=[("percent","percent"),("amount","amount")])
    value = models.DecimalField(max_digits=18, decimal_places=2)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    valid_from = models.DateField(null=True, blank=True)
    valid_to = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
