from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WarehouseViewSet, StockViewSet, StockMovementViewSet, StockTransferViewSet, StockTransferItemViewSet

router = DefaultRouter()
router.register("warehouses", WarehouseViewSet)
router.register("stock", StockViewSet)
router.register("movements", StockMovementViewSet)
router.register("transfers", StockTransferViewSet)
router.register("transfer-items", StockTransferItemViewSet)

urlpatterns = [path("", include(router.urls))]
