from django.contrib import admin
from .models import Warehouse, Stock, StockMovement, StockTransfer, StockTransferItem
admin.site.register(Warehouse)
admin.site.register(Stock)
admin.site.register(StockMovement)
admin.site.register(StockTransfer)
admin.site.register(StockTransferItem)

