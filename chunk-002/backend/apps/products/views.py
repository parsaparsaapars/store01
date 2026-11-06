from django.http import HttpResponse
from rest_framework import viewsets, permissions, parsers
from .models import Category, Brand, Unit, Product, PriceList, Discount
from .serializers import (CategorySerializer, BrandSerializer, UnitSerializer, ProductSerializer,
                          PriceListSerializer, DiscountSerializer)

def index(request):
    return HttpResponse("products app ok")

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all(); serializer_class = CategorySerializer; permission_classes=[permissions.IsAuthenticatedOrReadOnly]
class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all(); serializer_class = BrandSerializer; permission_classes=[permissions.IsAuthenticatedOrReadOnly]
class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all(); serializer_class = UnitSerializer; permission_classes=[permissions.IsAuthenticatedOrReadOnly]
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all(); serializer_class = ProductSerializer; permission_classes=[permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
class PriceListViewSet(viewsets.ModelViewSet):
    queryset = PriceList.objects.all(); serializer_class = PriceListSerializer; permission_classes=[permissions.IsAuthenticatedOrReadOnly]
class DiscountViewSet(viewsets.ModelViewSet):
    queryset = Discount.objects.all(); serializer_class = DiscountSerializer; permission_classes=[permissions.IsAuthenticatedOrReadOnly]
