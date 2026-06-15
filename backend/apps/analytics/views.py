from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncDate
from datetime import timedelta
from decimal import Decimal

from apps.wallets.models import Wallet
from apps.transactions.models import Transaction
from apps.refunds.models import Refund
from apps.notifications.models import Notification
from apps.accounts.models import User
from apps.accounts.permissions import IsAdmin
from .serializers import (
    DashboardStatsSerializer,
    AdminDashboardStatsSerializer,
    TransactionChartDataSerializer,
    RevenueStatsSerializer,
)


class UserDashboardStatsView(APIView):
    """
    GET /api/analytics/dashboard/
    Get dashboard statistics for the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            wallet = Wallet.objects.get(user=user)
        except Wallet.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Wallet not found',
                'data': None,
            }, status=404)

        # Calculate totals
        sent_transactions = Transaction.objects.filter(
            sender_wallet=wallet,
            transaction_type='transfer',
            status='completed'
        )
        received_transactions = Transaction.objects.filter(
            receiver_wallet=wallet,
            transaction_type='transfer',
            status='completed'
        )
        deposits = Transaction.objects.filter(
            sender_wallet=wallet,
            transaction_type='deposit',
            status='completed'
        )
        withdrawals = Transaction.objects.filter(
            sender_wallet=wallet,
            transaction_type='withdrawal',
            status='completed'
        )

        total_sent = sent_transactions.aggregate(
            total=Sum('amount', default=Decimal('0.00'))
        )['total']

        total_received = received_transactions.aggregate(
            total=Sum('amount', default=Decimal('0.00'))
        )['total']

        total_deposited = deposits.aggregate(
            total=Sum('amount', default=Decimal('0.00'))
        )['total']

        total_withdrawn = withdrawals.aggregate(
            total=Sum('amount', default=Decimal('0.00'))
        )['total']

        total_fees_paid = Transaction.objects.filter(
            sender_wallet=wallet,
            status='completed'
        ).aggregate(
            total=Sum('fee', default=Decimal('0.00'))
        )['total']

        # Count transactions
        transaction_count = Transaction.objects.filter(
            Q(sender_wallet=wallet) | Q(receiver_wallet=wallet)
        ).count()

        pending_transactions = Transaction.objects.filter(
            sender_wallet=wallet,
            status='pending'
        ).count()

        # Unread notifications
        unread_notifications = Notification.objects.filter(
            user=user,
            is_read=False
        ).count()

        stats = {
            'wallet_balance': wallet.balance,
            'total_sent': total_sent,
            'total_received': total_received,
            'total_deposited': total_deposited,
            'total_withdrawn': total_withdrawn,
            'total_fees_paid': total_fees_paid,
            'transaction_count': transaction_count,
            'pending_transactions': pending_transactions,
            'unread_notifications': unread_notifications,
        }

        serializer = DashboardStatsSerializer(stats)
        return Response({
            'success': True,
            'message': 'Dashboard stats retrieved successfully',
            'data': serializer.data,
        })


class AdminDashboardStatsView(APIView):
    """
    GET /api/analytics/admin/dashboard/
    Get dashboard statistics for admin users.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        # Total users
        total_users = User.objects.count()

        # Total wallets and balance
        wallet_stats = Wallet.objects.aggregate(
            total_wallets=Count('id'),
            total_balance=Sum('balance', default=Decimal('0.00')),
        )

        # Transaction stats
        transaction_stats = Transaction.objects.filter(
            status='completed'
        ).aggregate(
            total_transactions=Count('id'),
            total_volume=Sum('amount', default=Decimal('0.00')),
            total_fees=Sum('fee', default=Decimal('0.00')),
        )

        # Pending refunds
        pending_refunds = Refund.objects.filter(status='pending').count()

        # Active users today
        today = timezone.now().date()
        active_users_today = User.objects.filter(
            last_login__date=today
        ).count()

        # Frozen wallets
        frozen_wallets = Wallet.objects.filter(is_frozen=True).count()

        stats = {
            'total_users': total_users,
            'total_wallets': wallet_stats['total_wallets'],
            'total_balance': wallet_stats['total_balance'],
            'total_transactions': transaction_stats['total_transactions'],
            'total_transaction_volume': transaction_stats['total_volume'],
            'total_fees_collected': transaction_stats['total_fees'],
            'pending_refunds': pending_refunds,
            'active_users_today': active_users_today,
            'frozen_wallets': frozen_wallets,
        }

        serializer = AdminDashboardStatsSerializer(stats)
        return Response({
            'success': True,
            'message': 'Admin dashboard stats retrieved successfully',
            'data': serializer.data,
        })


class TransactionChartDataView(APIView):
    """
    GET /api/analytics/transactions-chart/
    Get transaction chart data for visualization.
    Supports date range filtering.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Get date range from query params
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now().date() - timedelta(days=days)

        # Get transactions for the user
        try:
            wallet = Wallet.objects.get(user=user)
            transactions = Transaction.objects.filter(
                Q(sender_wallet=wallet) | Q(receiver_wallet=wallet),
                status='completed',
                created_at__date__gte=start_date,
            )
        except Wallet.DoesNotExist:
            transactions = Transaction.objects.none()

        # Admin gets all transactions
        if user.role in ('admin', 'superadmin'):
            transactions = Transaction.objects.filter(
                status='completed',
                created_at__date__gte=start_date,
            )

        # Group by date
        chart_data = transactions.annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id'),
            volume=Sum('amount', default=Decimal('0.00')),
        ).order_by('date')

        serializer = TransactionChartDataSerializer(chart_data, many=True)
        return Response({
            'success': True,
            'message': 'Chart data retrieved successfully',
            'data': serializer.data,
        })


class RevenueStatsView(APIView):
    """
    GET /api/analytics/revenue/
    Get revenue statistics. Admin-only endpoint.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        now = timezone.now()
        today = now.date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        # Total revenue from fees
        total_revenue = Transaction.objects.filter(
            status='completed'
        ).aggregate(
            total=Sum('fee', default=Decimal('0.00'))
        )['total']

        # Today's revenue
        today_revenue = Transaction.objects.filter(
            status='completed',
            created_at__date=today
        ).aggregate(
            total=Sum('fee', default=Decimal('0.00'))
        )['total']

        # This week's revenue
        week_revenue = Transaction.objects.filter(
            status='completed',
            created_at__date__gte=week_ago
        ).aggregate(
            total=Sum('fee', default=Decimal('0.00'))
        )['total']

        # This month's revenue
        month_revenue = Transaction.objects.filter(
            status='completed',
            created_at__date__gte=month_ago
        ).aggregate(
            total=Sum('fee', default=Decimal('0.00'))
        )['total']

        # Revenue by transaction type
        revenue_by_type = {}
        for txn_type in ['transfer', 'withdrawal']:
            type_revenue = Transaction.objects.filter(
                status='completed',
                transaction_type=txn_type
            ).aggregate(
                total=Sum('fee', default=Decimal('0.00'))
            )['total']
            revenue_by_type[txn_type] = str(type_revenue)

        stats = {
            'total_revenue': total_revenue,
            'today_revenue': today_revenue,
            'week_revenue': week_revenue,
            'month_revenue': month_revenue,
            'revenue_by_type': revenue_by_type,
        }

        serializer = RevenueStatsSerializer(stats)
        return Response({
            'success': True,
            'message': 'Revenue stats retrieved successfully',
            'data': serializer.data,
        })
