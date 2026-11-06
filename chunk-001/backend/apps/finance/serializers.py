from rest_framework import serializers
from .models import Cashbox, BankAccount, FinanceTransaction, Expense, Receivable, Payable

class CashboxSerializer(serializers.ModelSerializer):
    class Meta: model = Cashbox; fields = "__all__"
class BankAccountSerializer(serializers.ModelSerializer):
    class Meta: model = BankAccount; fields = "__all__"
class FinanceTransactionSerializer(serializers.ModelSerializer):
    class Meta: model = FinanceTransaction; fields = "__all__"
class ExpenseSerializer(serializers.ModelSerializer):
    class Meta: model = Expense; fields = "__all__"
class ReceivableSerializer(serializers.ModelSerializer):
    class Meta: model = Receivable; fields = "__all__"
class PayableSerializer(serializers.ModelSerializer):
    class Meta: model = Payable; fields = "__all__"
