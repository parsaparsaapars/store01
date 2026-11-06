from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from apps.products.models import Product
from apps.customers.models import Customer
from apps.sales.models import Invoice
from apps.purchases.models import Supplier

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def global_search(request):
    q = request.GET.get("q", "")
    results = {"products": [], "customers": [], "invoices": [], "suppliers": []}
    if q:
        results["products"] = list(Product.objects.filter(Q(name__icontains=q)|Q(sku__icontains=q)|Q(barcode__icontains=q)).values("id","name","sku")[:10])
        results["customers"] = list(Customer.objects.filter(Q(name__icontains=q)|Q(phone__icontains=q)).values("id","name","phone")[:10])
        results["invoices"] = list(Invoice.objects.filter(invoice_no__icontains=q).values("id","invoice_no")[:10])
        results["suppliers"] = list(Supplier.objects.filter(Q(company_name__icontains=q)|Q(phone__icontains=q)).values("id","company_name")[:10])
    return JsonResponse(results)

def index(request):
    return HttpResponse("search app ok")
