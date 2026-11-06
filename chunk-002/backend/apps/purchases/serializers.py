from rest_framework import serializers
from .models import Supplier, PurchaseOrder, PurchaseItem, PurchaseReceipt

class SupplierSerializer(serializers.ModelSerializer):
    class Meta: model = Supplier; fields = "__all__"
class PurchaseItemSerializer(serializers.ModelSerializer):
    class Meta: model = PurchaseItem; fields = "__all__"
class PurchaseOrderSerializer(serializers.ModelSerializer):
    items = PurchaseItemSerializer(many=True, read_only=True)
    class Meta: model = PurchaseOrder; fields = "__all__"
class PurchaseReceiptSerializer(serializers.ModelSerializer):
    class Meta: model = PurchaseReceipt; fields = "__all__"
