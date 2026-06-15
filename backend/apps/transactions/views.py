from django.db import models as db_models
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import get_user_model

from .models import Transaction
from .serializers import (
    TransactionSerializer,
    TransactionListSerializer,
    SendMoneySerializer,
    DepositSerializer,
    CancelTransactionSerializer,
)
from .services import TransactionService
from .permissions import IsTransactionParticipant, IsSenderOrAdmin
from apps.wallets.models import Wallet
from apps.accounts.permissions import IsAdmin
from core.utils import (
    InsufficientFundsError,
    WalletFrozenError,
    WalletInactiveError,
    TransactionLimitError,
    InvalidTransactionError,
)

User = get_user_model()


class SendMoneyView(APIView):
    """
    POST /api/transactions/send/
    Send money from the authenticated user's wallet to another wallet.
    Uses transaction.atomic() with rollback on failure.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SendMoneySerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        sender_wallet = serializer.context['sender_wallet']
        receiver_wallet = serializer.context['receiver_wallet']
        amount = serializer.validated_data['amount']
        description = serializer.validated_data.get('description', '')
        fee = serializer.context['fee']

        try:
            transaction = TransactionService.send_money(
                sender_wallet=sender_wallet,
                receiver_wallet=receiver_wallet,
                amount=amount,
                description=description,
                fee=fee,
            )

            txn_serializer = TransactionSerializer(transaction)
            return Response({
                'success': True,
                'message': f'${amount:.2f} sent successfully to {receiver_wallet.user.username}',
                'data': txn_serializer.data,
            }, status=status.HTTP_201_CREATED)

        except InsufficientFundsError as e:
            return Response({
                'success': False,
                'message': str(e),
                'data': None,
            }, status=status.HTTP_400_BAD_REQUEST)
        except (WalletFrozenError, WalletInactiveError) as e:
            return Response({
                'success': False,
                'message': str(e),
                'data': None,
            }, status=status.HTTP_400_BAD_REQUEST)
        except TransactionLimitError as e:
            return Response({
                'success': False,
                'message': str(e),
                'data': None,
            }, status=status.HTTP_400_BAD_REQUEST)
        except InvalidTransactionError as e:
            return Response({
                'success': False,
                'message': str(e),
                'data': None,
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'An unexpected error occurred. Please try again.',
                'data': None,
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DepositView(APIView):
    """
    POST /api/transactions/deposit/
    Deposit money into the authenticated user's wallet.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DepositSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            wallet = Wallet.objects.get(user=request.user)
        except Wallet.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Wallet not found',
                'data': None,
            }, status=status.HTTP_404_NOT_FOUND)

        amount = serializer.validated_data['amount']
        description = serializer.validated_data.get('description', '')

        try:
            transaction = TransactionService.deposit(
                wallet=wallet,
                amount=amount,
                description=description,
            )

            txn_serializer = TransactionSerializer(transaction)
            return Response({
                'success': True,
                'message': f'${amount:.2f} deposited successfully',
                'data': txn_serializer.data,
            }, status=status.HTTP_201_CREATED)

        except (WalletFrozenError, WalletInactiveError, InvalidTransactionError) as e:
            return Response({
                'success': False,
                'message': str(e),
                'data': None,
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'An unexpected error occurred. Please try again.',
                'data': None,
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TransactionListView(generics.ListAPIView):
    """
    GET /api/transactions/
    List transactions for the authenticated user.
    Supports filtering by status, type, and date range.
    """
    serializer_class = TransactionListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        try:
            wallet = Wallet.objects.get(user=user)
        except Wallet.DoesNotExist:
            return Transaction.objects.none()

        queryset = Transaction.objects.filter(
            db_models.Q(sender_wallet=wallet) | db_models.Q(receiver_wallet=wallet)
        ).order_by('-created_at')

        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by transaction type
        type_filter = self.request.query_params.get('type', None)
        if type_filter:
            queryset = queryset.filter(transaction_type=type_filter)

        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        # Search by reference number
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(reference_number__icontains=search)

        return queryset


class TransactionDetailView(APIView):
    """
    GET /api/transactions/{id}/
    Retrieve details of a specific transaction.
    Only accessible by transaction participants or admins.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            transaction = Transaction.objects.get(pk=pk)
        except Transaction.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Transaction not found',
                'data': None,
            }, status=status.HTTP_404_NOT_FOUND)

        # Check permission
        if not (request.user.role in ('admin', 'superadmin') or
                transaction.sender_wallet.user == request.user or
                transaction.receiver_wallet.user == request.user):
            return Response({
                'success': False,
                'message': 'You do not have permission to view this transaction',
                'data': None,
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = TransactionSerializer(transaction)
        return Response({
            'success': True,
            'message': 'Transaction retrieved successfully',
            'data': serializer.data,
        })


class CancelTransactionView(APIView):
    """
    POST /api/transactions/{id}/cancel/
    Cancel a pending transaction.
    Only the sender or admin can cancel.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            transaction = Transaction.objects.get(pk=pk)
        except Transaction.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Transaction not found',
                'data': None,
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            updated_txn = TransactionService.cancel_transaction(transaction, request.user)
            serializer = TransactionSerializer(updated_txn)
            return Response({
                'success': True,
                'message': 'Transaction cancelled successfully',
                'data': serializer.data,
            })
        except InvalidTransactionError as e:
            return Response({
                'success': False,
                'message': str(e),
                'data': None,
            }, status=status.HTTP_400_BAD_REQUEST)


class AdminTransactionListView(generics.ListAPIView):
    """
    GET /api/transactions/admin/all/
    Admin-only endpoint to list all transactions.
    """
    serializer_class = TransactionListSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        queryset = Transaction.objects.all().order_by('-created_at')

        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by transaction type
        type_filter = self.request.query_params.get('type', None)
        if type_filter:
            queryset = queryset.filter(transaction_type=type_filter)

        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        # Search by reference number or username
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                db_models.Q(reference_number__icontains=search) |
                db_models.Q(sender_wallet__user__username__icontains=search) |
                db_models.Q(receiver_wallet__user__username__icontains=search)
            )

        return queryset
