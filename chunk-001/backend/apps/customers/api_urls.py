from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, CustomerPaymentViewSet

router = DefaultRouter()
router.register("customers", CustomerViewSet)
router.register("payments", CustomerPaymentViewSet)

urlpatterns = [path("", include(router.urls))]
