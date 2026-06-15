from rest_framework import serializers
from decimal import Decimal


class DashboardStatsSerializer(serializers.Serializer):
    """
    Serializer for user dashboard statistics.
    """

    wallet_balance = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_sent = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_received = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_deposited = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_withdrawn = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_fees_paid = serializers.DecimalField(max_digits=15, decimal_places=2)
    transaction_count = serializers.IntegerField()
    pending_transactions = serializers.IntegerField()
    unread_notifications = serializers.IntegerField()


class AdminDashboardStatsSerializer(serializers.Serializer):
    """
    Serializer for admin dashboard statistics.
    """

    total_users = serializers.IntegerField()
    total_wallets = serializers.IntegerField()
    total_balance = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_transactions = serializers.IntegerField()
    total_transaction_volume = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_fees_collected = serializers.DecimalField(max_digits=15, decimal_places=2)
    pending_refunds = serializers.IntegerField()
    active_users_today = serializers.IntegerField()
    frozen_wallets = serializers.IntegerField()


class TransactionChartDataSerializer(serializers.Serializer):
    """
    Serializer for transaction chart data.
    Returns data points for chart visualization.
    """

    date = serializers.DateField()
    count = serializers.IntegerField()
    volume = serializers.DecimalField(max_digits=15, decimal_places=2)


class RevenueStatsSerializer(serializers.Serializer):
    """
    Serializer for revenue statistics.
    """

    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    today_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    week_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    month_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    revenue_by_type = serializers.DictField()
