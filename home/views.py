from rest_framework import generics
from .models import Bank, Customer, Account, Deposit, Transaction, Withdraw
from .serializers import BankSerializer, CustomerSerializer, AccountSerializer, DepositSerializer, TransactionSerializer, WithdrawSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import ValidationError
from django.db import transaction as db_transaction
from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal


# Existing Views (No changes)

class BankListCreateView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Bank.objects.all()
    serializer_class = BankSerializer


class CustomerListCreateView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class AccountListCreateView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class DepositListCreateView(generics.ListCreateAPIView):
    serializer_class = DepositSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Deposit.objects.filter(account__user=self.request.user)

    def perform_create(self, serializer):
        account_id = serializer.validated_data['account'].id
        account = Account.objects.filter(user=self.request.user, id=account_id).first()
        if not account:
            raise ValidationError("Account not found or you don't have access to this account.")
        serializer.save(account=account)


class WithdrawListCreateView(generics.ListCreateAPIView):
    serializer_class = WithdrawSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return Withdraw.objects.filter(account__user=self.request.user)

    def perform_create(self, serializer):
        account_id = serializer.validated_data['account'].id
        account = Account.objects.filter(user=self.request.user, id=account_id).first()
        if not account:
            raise ValidationError("Account not found or you don't have access to this account.")
        serializer.save(account=account, user=self.request.user)  # Ensure user is set

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from django.utils.timezone import now
from .models import Account, Transaction
from decimal import Decimal

# TransferAPIView (POST) for making a transfer and GET to fetch transactions or account details
class TransferAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    # POST Method for making a transfer
    def post(self, request, *args, **kwargs):
        account_from_id = request.data.get('account_from')
        account_to_id = request.data.get('account_to')
        amount = request.data.get('amount')  # This is likely a float or string

        try:
            with db_transaction.atomic():
                # Validate accounts
                account_from = Account.objects.get(id=account_from_id)
                account_to = Account.objects.get(id=account_to_id)

                # Convert amount to Decimal
                amount = Decimal(amount)
                if account_from == account_to:
                    return Response({"error": "Cannot transfer to the same account."}, status=status.HTTP_400_BAD_REQUEST)

                if account_from.balance < amount:
                    return Response({"error": "Insufficient funds."}, status=status.HTTP_400_BAD_REQUEST)

                # Update balances
                account_from.balance -= amount
                account_to.balance += amount
                account_from.save()
                account_to.save()

                # Create transaction record
                Transaction.objects.create(
                    account_from=account_from,
                    account_to=account_to,
                    amount=amount,
                    transaction_date=now(),
                )

                return Response({"message": "Transaction successful."}, status=status.HTTP_200_OK)

        except Account.DoesNotExist:
            return Response({"error": "One or both accounts do not exist."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # GET Method for fetching recent transactions or account data
    def get(self, request, *args, **kwargs):
        user = request.user  # Get the authenticated user
        account_id = request.query_params.get('account_id', None)  # Optional account filter
        
        # Fetch transactions for the user
        transactions = Transaction.objects.filter(account_from__user=user).order_by('-transaction_date')[:10]  # Fetch last 10 transactions

        # If account_id is provided, filter transactions for that account
        if account_id:
            transactions = transactions.filter(account_from__id=account_id)  # Filter by account_id
        
        # Format transaction data for display
        transaction_data = [
            {
                "account_from": transaction.account_from.id,
                "account_to": transaction.account_to.id,
                "amount": str(transaction.amount),  # Convert Decimal to string for JSON serialization
                "transaction_date": transaction.transaction_date.isoformat(),
            }
            for transaction in transactions
        ]
        
        return Response({"transactions": transaction_data}, status=status.HTTP_200_OK)
