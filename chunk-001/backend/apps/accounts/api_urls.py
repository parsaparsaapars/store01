from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RoleViewSet, AuditLogViewSet, current_user, password_reset_request

router = DefaultRouter()
router.register("users", UserViewSet)
router.register("roles", RoleViewSet)
router.register("audit-logs", AuditLogViewSet)

urlpatterns = [
    path("me/", current_user),
    path("password-reset/request/", password_reset_request),
    path("", include(router.urls)),
]