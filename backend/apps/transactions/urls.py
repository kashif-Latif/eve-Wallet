from django.urls import path

from .views import (
    SendMoneyView,
    DepositView,
    TransactionListView,
    TransactionDetailView,
    CancelTransactionView,
    AdminTransactionListView,
)

app_name = 'transactions'

urlpatterns = [
    # User endpoints
    path('send/', SendMoneyView.as_view(), name='send_money'),
    path('deposit/', DepositView.as_view(), name='deposit'),
    path('', TransactionListView.as_view(), name='transaction_list'),
    path('<int:pk>/', TransactionDetailView.as_view(), name='transaction_detail'),
    path('<int:pk>/cancel/', CancelTransactionView.as_view(), name='cancel_transaction'),

    # Admin endpoints
    path('admin/all/', AdminTransactionListView.as_view(), name='admin_all_transactions'),
]
