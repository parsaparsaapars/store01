from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),
    path("products/", include("apps.products.urls", namespace="products")),
    path("inventory/", include("apps.inventory.urls", namespace="inventory")),
    path("sales/", include("apps.sales.urls", namespace="sales")),
    path("purchases/", include("apps.purchases.urls", namespace="purchases")),
    path("customers/", include("apps.customers.urls", namespace="customers")),
    path("finance/", include("apps.finance.urls", namespace="finance")),
    path("reports/", include("apps.reports.urls", namespace="reports")),
    path("notifications/", include("apps.notifications.urls", namespace="notifications")),
    path("settings/", include("apps.settings_app.urls", namespace="settings")),
    path("search/", include("apps.search.urls", namespace="search")),
    path("api/", include("config.api_urls")),
    path("", include("apps.core.urls", namespace="core")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
