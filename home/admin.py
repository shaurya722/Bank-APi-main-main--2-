from django.contrib import admin
from .models import Bank, Customer, Account, Transaction, BankCustomer, Deposit, Withdraw

# Register the Bank model
@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ('bank_name', 'location')
    search_fields = ('bank_name',)

# Register the Customer model
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'contact_info')
    search_fields = ('customer_name',)

# Register the Account model
@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'account_type', 'balance', 'customer', 'bank')
    search_fields = ('id', 'account_type', 'customer__customer_name', 'bank__bank_name')
    list_filter = ('account_type',)

# Register the Transaction model
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_type','account_from', 'bank_from', 'account_to', 'bank_to' ,'amount','transaction_date')
    search_fields = ('account__id', 'bank__bank_name', 'transaction_type')
    list_filter = ('transaction_type',)

# Register the BankCustomer model
@admin.register(BankCustomer)
class BankCustomerAdmin(admin.ModelAdmin):
    list_display = ('bank', 'customer')
    search_fields = ('bank__bank_name', 'customer__customer_name')

# Register the Deposit model
@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ('account', 'amount', 'transaction_date', 'status')
    search_fields = ('account__id', 'status')
    list_filter = ('status',)

# Register the Withdraw model
@admin.register(Withdraw)
class WithdrawAdmin(admin.ModelAdmin):
    list_display = ('account', 'amount', 'transaction_date', 'status')
    search_fields = ('account__id', 'status')
    list_filter = ('status',)
