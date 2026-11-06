from django.contrib import admin
from .models import Invoice, InvoiceItem, InvoicePayment, SalesReturn, SalesReturnItem
admin.site.register(Invoice)
admin.site.register(InvoiceItem)
admin.site.register(InvoicePayment)
admin.site.register(SalesReturn)
admin.site.register(SalesReturnItem)

