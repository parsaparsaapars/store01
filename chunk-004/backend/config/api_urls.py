from django.urls import path, include

urlpatterns = [
    path("accounts/", include("apps.accounts.api_urls")),
    path("customers/", include("apps.customers.api_urls")),
    path("products/", include("apps.products.api_urls")),
    path("search/", include("apps.search.api_urls")),
    path("sales/", include("apps.sales.api_urls")),
    path("inventory/", include("apps.inventory.api_urls")),
]
