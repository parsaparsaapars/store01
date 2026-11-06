from django.http import HttpResponse
from rest_framework import viewsets, permissions
from .models import Customer, CustomerPayment
from .serializers import CustomerSerializer, CustomerPaymentSerializer

def index(request):
    return HttpResponse("customers app ok")

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all(); serializer_class = CustomerSerializer; permission_classes=[permissions.IsAuthenticatedOrReadOnly]
class CustomerPaymentViewSet(viewsets.ModelViewSet):
    queryset = CustomerPayment.objects.all(); serializer_class = CustomerPaymentSerializer; permission_classes=[permissions.IsAuthenticatedOrReadOnly]
