from django.contrib import admin
from .models import Supplier, PurchaseOrder, PurchaseItem, PurchaseReceipt
admin.site.register(Supplier)
admin.site.register(PurchaseOrder)
admin.site.register(PurchaseItem)
admin.site.register(PurchaseReceipt)

