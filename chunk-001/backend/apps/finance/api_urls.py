from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (CashboxViewSet, BankAccountViewSet, FinanceTransactionViewSet,
                    ExpenseViewSet, ReceivableViewSet, PayableViewSet)

router = DefaultRouter()
router.register("cashboxes", CashboxViewSet)
router.register("bank-accounts", BankAccountViewSet)
router.register("transactions", FinanceTransactionViewSet)
router.register("expenses", ExpenseViewSet)
router.register("receivables", ReceivableViewSet)
router.register("payables", PayableViewSet)

urlpatterns = [path("", include(router.urls))]
