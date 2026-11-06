from rest_framework import serializers
from .models import Category, Brand, Unit, Product, PriceList, Discount

class CategorySerializer(serializers.ModelSerializer):
    class Meta: model = Category; fields = "__all__"
class BrandSerializer(serializers.ModelSerializer):
    class Meta: model = Brand; fields = "__all__"
class UnitSerializer(serializers.ModelSerializer):
    class Meta: model = Unit; fields = "__all__"
class ProductSerializer(serializers.ModelSerializer):
    class Meta: model = Product; fields = "__all__"
class PriceListSerializer(serializers.ModelSerializer):
    class Meta: model = PriceList; fields = "__all__"
class DiscountSerializer(serializers.ModelSerializer):
    class Meta: model = Discount; fields = "__all__"
