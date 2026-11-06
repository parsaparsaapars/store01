from django.http import HttpResponse
from rest_framework import viewsets, permissions
from .models import Cashbox, BankAccount, FinanceTransaction, Expense, Receivable, Payable
from .serializers import (CashboxSerializer, BankAccountSerializer, FinanceTransactionSerializer,
                          ExpenseSerializer, ReceivableSerializer, PayableSerializer)

def index(request):
    return HttpResponse("finance app ok")

class CashboxViewSet(viewsets.ModelViewSet):
    queryset = Cashbox.objects.all(); serializer_class = CashboxSerializer; permission_classes=[permissions.IsAuthenticated]
class BankAccountViewSet(viewsets.ModelViewSet):
    queryset = BankAccount.objects.all(); serializer_class = BankAccountSerializer; permission_classes=[permissions.IsAuthenticated]
class FinanceTransactionViewSet(viewsets.ModelViewSet):
    queryset = FinanceTransaction.objects.all(); serializer_class = FinanceTransactionSerializer; permission_classes=[permissions.IsAuthenticated]
class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all(); serializer_class = ExpenseSerializer; permission_classes=[permissions.IsAuthenticated]
class ReceivableViewSet(viewsets.ModelViewSet):
    queryset = Receivable.objects.all(); serializer_class = ReceivableSerializer; permission_classes=[permissions.IsAuthenticated]
class PayableViewSet(viewsets.ModelViewSet):
    queryset = Payable.objects.all(); serializer_class = PayableSerializer; permission_classes=[permissions.IsAuthenticated]
