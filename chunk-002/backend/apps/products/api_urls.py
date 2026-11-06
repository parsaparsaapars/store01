from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, BrandViewSet, UnitViewSet, ProductViewSet, PriceListViewSet, DiscountViewSet

router = DefaultRouter()
router.register("categories", CategoryViewSet)
router.register("brands", BrandViewSet)
router.register("units", UnitViewSet)
router.register("products", ProductViewSet)
router.register("prices", PriceListViewSet)
router.register("discounts", DiscountViewSet)

urlpatterns = [path("", include(router.urls))]
