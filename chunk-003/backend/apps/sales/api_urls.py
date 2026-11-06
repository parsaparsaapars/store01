from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InvoiceViewSet, InvoiceItemViewSet, InvoicePaymentViewSet, SalesReturnViewSet, SalesReturnItemViewSet, pos_checkout

router = DefaultRouter()
router.register("invoices", InvoiceViewSet)
router.register("invoice-items", InvoiceItemViewSet)
router.register("invoice-payments", InvoicePaymentViewSet)
router.register("returns", SalesReturnViewSet)
router.register("return-items", SalesReturnItemViewSet)

urlpatterns = [
    path("pos-checkout/", pos_checkout),
    path("", include(router.urls)),
]
