from django.urls import path

from .views import (
    MyWalletView,
    WalletBalanceView,
    FreezeWalletView,
    WalletTransactionsView,
    AdminWalletListView,
    AdminUpdateWalletLimitsView,
)

app_name = 'wallets'

urlpatterns = [
    # User endpoints
    path('my-wallet/', MyWalletView.as_view(), name='my_wallet'),
    path('balance/', WalletBalanceView.as_view(), name='balance'),
    path('transactions/', WalletTransactionsView.as_view(), name='transactions'),

    # Admin endpoints
    path('admin/all/', AdminWalletListView.as_view(), name='admin_all_wallets'),
    path('<int:pk>/freeze/', FreezeWalletView.as_view(), name='freeze_wallet'),
    path('<int:pk>/update-limits/', AdminUpdateWalletLimitsView.as_view(), name='update_limits'),
]
