from django.contrib import admin
from .models import Cashbox, BankAccount, FinanceTransaction, Expense, Receivable, Payable
admin.site.register(Cashbox)
admin.site.register(BankAccount)
admin.site.register(FinanceTransaction)
admin.site.register(Expense)
admin.site.register(Receivable)
admin.site.register(Payable)

