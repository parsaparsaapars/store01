from django.http import HttpResponse
from rest_framework import viewsets, permissions
from .models import Warehouse, Stock, StockMovement, StockTransfer, StockTransferItem
from .serializers import WarehouseSerializer, StockSerializer, StockMovementSerializer, StockTransferSerializer, StockTransferItemSerializer

def index(request):
    return HttpResponse("inventory app ok")

class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all(); serializer_class = WarehouseSerializer; permission_classes=[permissions.IsAuthenticatedOrReadOnly]
class StockViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stock.objects.all(); serializer_class = StockSerializer; permission_classes=[permissions.IsAuthenticatedOrReadOnly]
class StockMovementViewSet(viewsets.ModelViewSet):
    queryset = StockMovement.objects.all(); serializer_class = StockMovementSerializer; permission_classes=[permissions.IsAuthenticatedOrReadOnly]
class StockTransferViewSet(viewsets.ModelViewSet):
    queryset = StockTransfer.objects.all(); serializer_class = StockTransferSerializer; permission_classes=[permissions.IsAuthenticatedOrReadOnly]
class StockTransferItemViewSet(viewsets.ModelViewSet):
    queryset = StockTransferItem.objects.all(); serializer_class = StockTransferItemSerializer; permission_classes=[permissions.IsAuthenticatedOrReadOnly]
