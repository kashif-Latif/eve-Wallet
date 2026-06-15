from django.db import models as db_models
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from django.contrib.auth import get_user_model

from .models import Wallet
from .serializers import (
    WalletSerializer,
    WalletBalanceSerializer,
    FreezeWalletSerializer,
    UpdateWalletLimitsSerializer,
)
from .permissions import IsWalletOwnerOrAdmin
from .services import WalletService
from apps.accounts.permissions import IsAdmin

User = get_user_model()


class MyWalletView(APIView):
    """
    GET /api/wallets/my-wallet/
    Retrieve the authenticated user's wallet details.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            wallet = Wallet.objects.get(user=request.user)
            serializer = WalletSerializer(wallet)
            return Response({
                'success': True,
                'message': 'Wallet retrieved successfully',
                'data': serializer.data,
            })
        except Wallet.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Wallet not found',
                'data': None,
            }, status=status.HTTP_404_NOT_FOUND)


class WalletBalanceView(APIView):
    """
    GET /api/wallets/balance/
    Retrieve the authenticated user's wallet balance.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            wallet = Wallet.objects.get(user=request.user)
            serializer = WalletBalanceSerializer(wallet)
            return Response({
                'success': True,
                'message': 'Balance retrieved successfully',
                'data': serializer.data,
            })
        except Wallet.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Wallet not found',
                'data': None,
            }, status=status.HTTP_404_NOT_FOUND)


class FreezeWalletView(APIView):
    """
    POST /api/wallets/{id}/freeze/
    Freeze or unfreeze a wallet. Admin-only operation.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, pk):
        try:
            wallet = Wallet.objects.get(pk=pk)
        except Wallet.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Wallet not found',
                'data': None,
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = FreezeWalletSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action = serializer.validated_data['action']
        reason = serializer.validated_data.get('reason', '')

        try:
            if action == 'freeze':
                wallet = WalletService.freeze_wallet(wallet, request.user, reason)
                message = f'Wallet {wallet.wallet_number} has been frozen.'
            else:
                wallet = WalletService.unfreeze_wallet(wallet, request.user, reason)
                message = f'Wallet {wallet.wallet_number} has been unfrozen.'

            wallet_serializer = WalletSerializer(wallet)
            return Response({
                'success': True,
                'message': message,
                'data': wallet_serializer.data,
            })
        except ValueError as e:
            return Response({
                'success': False,
                'message': str(e),
                'data': None,
            }, status=status.HTTP_400_BAD_REQUEST)


class WalletTransactionsView(APIView):
    """
    GET /api/wallets/transactions/
    Retrieve transaction history for the authenticated user's wallet.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            wallet = Wallet.objects.get(user=request.user)
            from apps.transactions.models import Transaction
            from apps.transactions.serializers import TransactionListSerializer

            # Get transactions where user is sender or receiver
            transactions = Transaction.objects.filter(
                db_models.Q(sender_wallet=wallet) | db_models.Q(receiver_wallet=wallet)
            ).order_by('-created_at')

            # Filter by status
            status_filter = request.query_params.get('status', None)
            if status_filter:
                transactions = transactions.filter(status=status_filter)

            # Filter by type
            type_filter = request.query_params.get('type', None)
            if type_filter:
                transactions = transactions.filter(transaction_type=type_filter)

            # Date range filter
            start_date = request.query_params.get('start_date', None)
            end_date = request.query_params.get('end_date', None)
            if start_date:
                transactions = transactions.filter(created_at__date__gte=start_date)
            if end_date:
                transactions = transactions.filter(created_at__date__lte=end_date)

            # Paginate
            paginator = PageNumberPagination()
            paginator.page_size = 20
            page = paginator.paginate_queryset(transactions, request)

            serializer = TransactionListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        except Wallet.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Wallet not found',
                'data': None,
            }, status=status.HTTP_404_NOT_FOUND)


class AdminWalletListView(generics.ListAPIView):
    """
    GET /api/wallets/admin/all/
    Admin-only endpoint to list all wallets.
    """
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        queryset = Wallet.objects.all().order_by('-created_at')

        # Filter by active status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            is_active_bool = is_active.lower() in ('true', '1', 'yes')
            queryset = queryset.filter(is_active=is_active_bool)

        # Filter by frozen status
        is_frozen = self.request.query_params.get('is_frozen', None)
        if is_frozen is not None:
            is_frozen_bool = is_frozen.lower() in ('true', '1', 'yes')
            queryset = queryset.filter(is_frozen=is_frozen_bool)

        # Search by wallet number or username
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                db_models.Q(wallet_number__icontains=search) |
                db_models.Q(user__username__icontains=search) |
                db_models.Q(user__email__icontains=search)
            )

        return queryset


class AdminUpdateWalletLimitsView(APIView):
    """
    PUT /api/wallets/{id}/update-limits/
    Admin-only endpoint to update wallet limits.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def put(self, request, pk):
        try:
            wallet = Wallet.objects.get(pk=pk)
        except Wallet.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Wallet not found',
                'data': None,
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = UpdateWalletLimitsSerializer(wallet, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        wallet_serializer = WalletSerializer(wallet)
        return Response({
            'success': True,
            'message': 'Wallet limits updated successfully',
            'data': wallet_serializer.data,
        })
