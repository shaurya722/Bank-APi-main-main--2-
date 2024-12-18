from rest_framework import generics

from api.models import User
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

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Account

# Existing Views (No changes)

class BankListCreateView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = BankSerializer
    def get_queryset(self):
        user = self.request.user
        print(user)  
        if user.is_staff:
            return Account.objects.all()
        else:
            return Account.objects.filter(user=user)



class CustomerListCreateView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = CustomerSerializer
    def get_queryset(self):
        user = self.request.user
        print(user)  
        if user.is_staff:
            return Customer.objects.all()
        else:
            return Customer.objects.filter(user=user)


class CustomerRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerSerializer

    def get_queryset(self):
        user = self.request.user
        print(user)  
        if user.is_staff:
            return Customer.objects.all()
        else:
            return Customer.objects.filter(user=user)


class AccountListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]    
    serializer_class = AccountSerializer

    def get_queryset(self):
        user = self.request.user
        print(user)  
        if user.is_staff:
            return Account.objects.all()
        else:
            return Account.objects.filter(user=user)
        

@api_view(['POST'])
def create_account(request):
    # Ensure that the user field is in the request data
    user_id = request.data.get('user')
    if not user_id:
        return Response({"detail": "User field is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Optionally, you can validate if the user exists in the database
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    # Add the user to the data to be serialized
    data = request.data
    data['user'] = user.id  # Make sure to pass the valid user ID

    serializer = AccountSerializer(data=data)
    if serializer.is_valid():
        account = serializer.save()  # Save the account with the provided user
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AccountRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]    
    serializer_class = AccountSerializer

    def get_queryset(self):
        user = self.request.user
        print(user)  
        if user.is_staff:
            return Account.objects.all()
        else:
            return Account.objects.filter(user=user)



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


    #    from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Account, Transaction
from .serializers import AccountSerializer  # Assuming you have a serializer for Account
# from .authentication import JWTAuthentication
from django.utils.timezone import now
from decimal import Decimal
from django.db import transaction as db_transaction


class TransferAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    # GET Method to fetch all available accounts
    def get(self, request, *args, **kwargs):
        """
        Fetch all available accounts for selection as `account_to`.
        """
        accounts = Account.objects.all()  # Fetch all accounts
        serializer = AccountSerializer(accounts, many=True)  # Serialize account data
        return Response(serializer.data, status=status.HTTP_200_OK)

    # POST Method for making a transfer
    def post(self, request, *args, **kwargs):
        account_from_id = request.data.get('account_from')
        account_to_id = request.data.get('account_to')
        scheduled_time = request.data.get('scheduled_time')
        amount = request.data.get('amount')

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
                    scheduled_time=scheduled_time,
                    amount=amount,
                    transaction_date=now(),
                )

                return Response({"message": "Transaction successful."}, status=status.HTTP_200_OK)

        except Account.DoesNotExist:
            return Response({"error": "One or both accounts do not exist."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
