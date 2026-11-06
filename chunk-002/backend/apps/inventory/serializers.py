from rest_framework import serializers
from .models import Warehouse, Stock, StockMovement, StockTransfer, StockTransferItem

class WarehouseSerializer(serializers.ModelSerializer):
    class Meta: model = Warehouse; fields = "__all__"
class StockSerializer(serializers.ModelSerializer):
    class Meta: model = Stock; fields = "__all__"
class StockMovementSerializer(serializers.ModelSerializer):
    class Meta: model = StockMovement; fields = "__all__"
class StockTransferItemSerializer(serializers.ModelSerializer):
    class Meta: model = StockTransferItem; fields = "__all__"
class StockTransferSerializer(serializers.ModelSerializer):
    items = StockTransferItemSerializer(many=True, read_only=True)
    class Meta: model = StockTransfer; fields = "__all__"
