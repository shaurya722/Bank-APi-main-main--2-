from rest_framework import serializers

from api.models import User
from .models import Bank, Customer, Account, Deposit, Transaction, Withdraw


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'transaction_date', 'transaction_type','account_from', 'bank_from', 'account_to', 'bank_to','amount']


class AccountSerializer(serializers.ModelSerializer):
    bank = serializers.StringRelatedField()
    transactions = TransactionSerializer(many=True, read_only=True)

    class Meta:
        model = Account
        fields = ['id', 'account_type', 'balance', 'bank', 'transactions']

# class BankCustomerSerializer(serializers.ModelSerializer):
#     customer = serializers.StringRelatedField()
#     bank = serializers.StringRelatedField()

#     class Meta:
#         model = BankCustomer
#         fields = ['id', 'bank', 'customer']


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'customer_name', 'contact_info', 'accounts']  
        depth = 3
        
class BankSerializer(serializers.ModelSerializer):
    accounts = AccountSerializer(many=True, read_only=True)  # Use the related_name 'accounts'
    transactions = TransactionSerializer(many=True, read_only=True)  # Use the related_name 'transactions'

    class Meta:
        model = Bank
        fields = ['id', 'bank_name', 'location', 'accounts', 'transactions']

class DepositSerializer(serializers.ModelSerializer):
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all(), required=False)  # Make account optional
    amount = serializers.DecimalField(max_digits=15, decimal_places=2, required=True)  # Make amount required
    # user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)  # Add user field

    class Meta:
        model = Deposit
        fields = ['id', 'account', 'amount', 'transaction_date', 'status']


class WithdrawSerializer(serializers.ModelSerializer):
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all(), required=True)  # Make account required
    amount = serializers.DecimalField(max_digits=15, decimal_places=2, required=True)  # Make amount required
    # user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)  # Add user field

    class Meta:
        model = Withdraw
        fields = ['id', 'account', 'amount', 'transaction_date', 'status']  # Include user field
