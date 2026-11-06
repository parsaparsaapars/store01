from django.contrib import admin
from .models import Category, Brand, Unit, Product, PriceList, Discount
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Unit)
admin.site.register(Product)
admin.site.register(PriceList)
admin.site.register(Discount)

