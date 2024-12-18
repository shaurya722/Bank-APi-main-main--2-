from django.urls import path

from .views import (
    AccountListView,
    AccountRetrieveUpdateDestroyView,
    BankListCreateView,
    CustomerListCreateView,
    # AccountListCreateView,
    CustomerRetrieveUpdateDestroyView,
    DepositListCreateView,
    # TransactionListCreateView,
    # BankCustomerListCreateView,
    TransferAPIView,
    WithdrawListCreateView,
    create_account,
)

urlpatterns = [
    path('banks/', BankListCreateView.as_view(), name='bank-list-create'),
    path('customers/', CustomerListCreateView.as_view(), name='customer-list-create'),
    path('customers/<int:pk>/', CustomerRetrieveUpdateDestroyView.as_view(), name='customer-detail'),

    # path('customers', CustomerListCreateView.as_view(), name='customer-list-create'),
    path('accounts/', AccountListView.as_view(), name='account-list'),
    path('accounts/create/', create_account, name='account-create'),
    path('accounts/<int:pk>/', AccountRetrieveUpdateDestroyView.as_view(), name='user-detail'),
    path('transactions/', TransferAPIView.as_view(), name='transaction-list-create'),
    # path('transactions/transfer/', TransferAPIView.as_view(), name='transfer'),  # POST request for transfers

    # path('bank-customers/', BankCustomerListCreateView.as_view(), name='bankcustomer-list-create'),
    path('withdraw/', WithdrawListCreateView.as_view(), name='withdraw-list-create'),
    path('deposit/', DepositListCreateView.as_view(), name='deposit-list-create'),
]
