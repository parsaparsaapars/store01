from django.db import models
from apps.core.models import TimeStampedModel

class Cashbox(TimeStampedModel):
    name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class BankAccount(TimeStampedModel):
    name = models.CharField(max_length=100)
    account_no = models.CharField(max_length=100, blank=True)
    balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

class FinanceTransaction(TimeStampedModel):
    TYPE = [("receipt","receipt"),("payment","payment"),("transfer","transfer")]
    tx_type = models.CharField(max_length=20, choices=TYPE)
    cashbox = models.ForeignKey(Cashbox, on_delete=models.SET_NULL, null=True, blank=True)
    bank_account = models.ForeignKey(BankAccount, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    party = models.CharField(max_length=200, blank=True)
    reference = models.CharField(max_length=100, blank=True)
    method = models.CharField(max_length=50, blank=True)
    note = models.TextField(blank=True)
    created_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True)

class Expense(TimeStampedModel):
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    category = models.CharField(max_length=100, blank=True)
    expense_date = models.DateField()
    note = models.TextField(blank=True)

class Receivable(TimeStampedModel):
    customer = models.ForeignKey("customers.Customer", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    due_date = models.DateField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)

class Payable(TimeStampedModel):
    supplier = models.ForeignKey("purchases.Supplier", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    due_date = models.DateField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
