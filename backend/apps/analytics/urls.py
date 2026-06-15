from django.urls import path

from .views import (
    UserDashboardStatsView,
    AdminDashboardStatsView,
    TransactionChartDataView,
    RevenueStatsView,
)

app_name = 'analytics'

urlpatterns = [
    # User analytics
    path('dashboard/', UserDashboardStatsView.as_view(), name='user_dashboard'),
    path('transactions-chart/', TransactionChartDataView.as_view(), name='transactions_chart'),

    # Admin analytics
    path('admin/dashboard/', AdminDashboardStatsView.as_view(), name='admin_dashboard'),
    path('revenue/', RevenueStatsView.as_view(), name='revenue'),
]
