from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SupplierViewSet, PurchaseOrderViewSet, PurchaseItemViewSet, PurchaseReceiptViewSet

router = DefaultRouter()
router.register("suppliers", SupplierViewSet)
router.register("orders", PurchaseOrderViewSet)
router.register("items", PurchaseItemViewSet)
router.register("receipts", PurchaseReceiptViewSet)

urlpatterns = [path("", include(router.urls))]
