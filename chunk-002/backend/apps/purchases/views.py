from django.http import HttpResponse
from rest_framework import viewsets, permissions
from .models import Supplier, PurchaseOrder, PurchaseItem, PurchaseReceipt
from .serializers import SupplierSerializer, PurchaseOrderSerializer, PurchaseItemSerializer, PurchaseReceiptSerializer

def index(request):
    return HttpResponse("purchases app ok")

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all(); serializer_class = SupplierSerializer; permission_classes=[permissions.IsAuthenticated]
class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all(); serializer_class = PurchaseOrderSerializer; permission_classes=[permissions.IsAuthenticated]
class PurchaseItemViewSet(viewsets.ModelViewSet):
    queryset = PurchaseItem.objects.all(); serializer_class = PurchaseItemSerializer; permission_classes=[permissions.IsAuthenticated]
class PurchaseReceiptViewSet(viewsets.ModelViewSet):
    queryset = PurchaseReceipt.objects.all(); serializer_class = PurchaseReceiptSerializer; permission_classes=[permissions.IsAuthenticated]
