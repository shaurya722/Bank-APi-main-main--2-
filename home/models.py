from django.db import models
from django.db import transaction
from api.models import User  # Assuming User model is imported from your app

class Bank(models.Model):
    bank_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.bank_name

    class Meta:
        verbose_name = "Bank"
        verbose_name_plural = "Banks"


class Customer(models.Model):
    
    customer_name = models.CharField(max_length=100)
    contact_info = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.customer_name

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"


class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='account', null=False)
    class AccountType(models.TextChoices):
        SAVINGS = 'SAVINGS', 'Savings'
        CURRENT = 'CURRENT', 'Current'
        FIXED = 'FIXED', 'Fixed'

    account_type = models.CharField(max_length=50, choices=AccountType.choices)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="accounts")
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name="accounts")

    def __str__(self):
        return f"{self.account_type} - {self.id}"

    def deposit(self, amount):
        """Deposit amount into the account."""
        if amount > 0:
            self.balance += amount
            self.save()

    def withdraw(self, amount):
        """Withdraw amount from the account if sufficient balance exists."""
        if amount > 0 and self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('DEBIT', 'Debit'),
        ('CREDIT', 'Credit'),
    ]
    transaction_date = models.DateTimeField(auto_now=True, blank=True)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    bank_from = models.ForeignKey(Bank,on_delete=models.CASCADE,related_name='transactions_from',null=True)
    account_from = models.ForeignKey(Account,on_delete=models.CASCADE,related_name='transactions_from',null=True,default='debit')
    bank_to =   models.ForeignKey(Bank, on_delete=models.CASCADE, related_name="transactions",null=True)
    account_to = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="transactions",null=True,default='credit')
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Transaction {self.id} - {self.transaction_type} on {self.transaction_date}"


class BankCustomer(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.bank.bank_name} - {self.customer.customer_name}"

    class Meta:
        unique_together = ('bank', 'customer')
        verbose_name = "Bank Customer"
        verbose_name_plural = "Bank Customers"


class Deposit(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="deposits")
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50, choices=[('PENDING', 'Pending'), ('COMPLETED', 'Completed')], default='PENDING')
    # user = models.ForeignKey(User, on_delete=models.CASCADE,default=False)  # Explicit user field

    def save(self, *args, **kwargs):
        if self.amount <= 0:
            raise ValueError("Deposit amount must be greater than zero.")
        
        # Check if account exists and if the user has access
        if not Account.objects.filter(id=self.account.id).exists():
            raise ValueError("Account does not exist.")
        
        # Ensure the user is the owner of the account
        # if self.account.user != self.user:
        #     raise ValueError("Account not found or you don't have access to this account.")
        
        with transaction.atomic():
            account = self.account
            account.deposit(self.amount)  # Update account balance
            self.status = 'COMPLETED'  # Mark deposit as completed
            # Create a transaction record
            Transaction.objects.create(
                transaction_type='CREDIT', 
                amount=self.amount, 
                # account=self.account, 
                # bank=self.account.bank
                account_from=None,
                account_to=self.account,
                bank_from=None,
                bank_to=self.account.bank
            )
            super().save(*args, **kwargs)

    def __str__(self):
        return f"Deposit {self.id} - Amount: {self.amount} on {self.transaction_date}"


class Withdraw(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="withdrawals")
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50, choices=[('PENDING', 'Pending'), ('COMPLETED', 'Completed')], default='PENDING')
    # user = models.ForeignKey(User, on_delete=models.CASCADE)  # Explicit user field

    def save(self, *args, **kwargs):
        if not self.user_id:
            raise ValueError("User must be set for the withdrawal.")
        
        with transaction.atomic():
            account = self.account
            # Ensure the user has access to the account
            # if account.user != self.user:
            #     raise ValueError("Account not found or you don't have access to this account.")
            
            if account.withdraw(self.amount):  # Try withdrawing
                self.status = 'COMPLETED'
                # Create a transaction record
                Transaction.objects.create(
                    transaction_type='DEBIT',
                    amount=self.amount,
                    account_from=self.account,
                    account_to=None,
                    bank_from=self.account.bank,
                    bank_to=None
                )
                super().save(*args, **kwargs)  # Save withdrawal if successful
            else:
                raise ValueError("Insufficient funds for withdrawal")  # If insufficient funds

    def __str__(self):
        return f"Withdraw {self.id} - Amount: {self.amount} on {self.transaction_date}"
