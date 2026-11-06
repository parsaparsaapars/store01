from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StoreSettingsViewSet

router = DefaultRouter()
router.register("store", StoreSettingsViewSet)

urlpatterns = [path("", include(router.urls))]
