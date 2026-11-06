from rest_framework import serializers
from .models import Invoice, InvoiceItem, InvoicePayment, SalesReturn, SalesReturnItem

class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta: model = InvoiceItem; fields = "__all__"
class InvoicePaymentSerializer(serializers.ModelSerializer):
    class Meta: model = InvoicePayment; fields = "__all__"
class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True)
    payments = InvoicePaymentSerializer(many=True, read_only=True)
    class Meta: model = Invoice; fields = "__all__"
class SalesReturnItemSerializer(serializers.ModelSerializer):
    class Meta: model = SalesReturnItem; fields = "__all__"
class SalesReturnSerializer(serializers.ModelSerializer):
    items = SalesReturnItemSerializer(many=True, read_only=True)
    class Meta: model = SalesReturn; fields = "__all__"
