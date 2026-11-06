from rest_framework import serializers
from .models import Customer, CustomerPayment

class CustomerSerializer(serializers.ModelSerializer):
    class Meta: model = Customer; fields = "__all__"
class CustomerPaymentSerializer(serializers.ModelSerializer):
    class Meta: model = CustomerPayment; fields = "__all__"
