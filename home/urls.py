from django.urls import path
from .views import (
    BankListCreateView,
    CustomerListCreateView,
    AccountListCreateView,
    DepositListCreateView,
    # TransactionListCreateView,
    # BankCustomerListCreateView,
    TransferAPIView,
    WithdrawListCreateView,
)

urlpatterns = [
    path('banks/', BankListCreateView.as_view(), name='bank-list-create'),
    path('customers/', CustomerListCreateView.as_view(), name='customer-list-create'),
    path('accounts/', AccountListCreateView.as_view(), name='account-list-create'),
    path('transactions/', TransferAPIView.as_view(), name='transaction-list-create'),
    # path('transactions/transfer/', TransferAPIView.as_view(), name='transfer'),  # POST request for transfers

    # path('bank-customers/', BankCustomerListCreateView.as_view(), name='bankcustomer-list-create'),
    path('withdraw/', WithdrawListCreateView.as_view(), name='withdraw-list-create'),
    path('deposit/', DepositListCreateView.as_view(), name='deposit-list-create'),
]
