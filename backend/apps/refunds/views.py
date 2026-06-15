from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import get_user_model

from .models import Refund
from .serializers import (
    RefundSerializer,
    RefundListSerializer,
    RequestRefundSerializer,
    ProcessRefundSerializer,
    CompleteRefundSerializer,
)
from .services import RefundService
from .permissions import IsRefundRequesterOrAdmin, IsAdminOnly
from core.utils import InvalidTransactionError, RefundError

User = get_user_model()


class RequestRefundView(APIView):
    """
    POST /api/refunds/request/
    Request a refund for a completed transaction.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RequestRefundSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        transaction = serializer.context['transaction']
        reason = serializer.validated_data['reason']
        amount = serializer.validated_data.get('amount')

        try:
            refund = RefundService.request_refund(
                user=request.user,
                transaction=transaction,
                reason=reason,
                amount=amount,
            )

            refund_serializer = RefundSerializer(refund)
            return Response({
                'success': True,
                'message': 'Refund request submitted successfully',
                'data': refund_serializer.data,
            }, status=status.HTTP_201_CREATED)

        except (InvalidTransactionError, RefundError) as e:
            return Response({
                'success': False,
                'message': str(e),
                'data': None,
            }, status=status.HTTP_400_BAD_REQUEST)


class MyRefundsListView(generics.ListAPIView):
    """
    GET /api/refunds/my-refunds/
    List all refund requests made by the authenticated user.
    """
    serializer_class = RefundListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Refund.objects.filter(
            requested_by=self.request.user
        ).order_by('-created_at')


class RefundListView(generics.ListAPIView):
    """
    GET /api/refunds/
    Admin-only endpoint to list all refund requests.
    """
    serializer_class = RefundListSerializer
    permission_classes = [IsAuthenticated, IsAdminOnly]

    def get_queryset(self):
        queryset = Refund.objects.all().order_by('-created_at')

        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Search by transaction reference
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                transaction__reference_number__icontains=search
            )

        return queryset


class ProcessRefundView(APIView):
    """
    POST /api/refunds/{id}/process/
    Admin-only endpoint to approve or reject a refund request.
    """
    permission_classes = [IsAuthenticated, IsAdminOnly]

    def post(self, request, pk):
        try:
            refund = Refund.objects.get(pk=pk)
        except Refund.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Refund not found',
                'data': None,
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ProcessRefundSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action = serializer.validated_data['action']
        admin_note = serializer.validated_data.get('admin_note', '')

        try:
            updated_refund = RefundService.process_refund(
                refund=refund,
                admin_user=request.user,
                action=action,
                admin_note=admin_note,
            )

            refund_serializer = RefundSerializer(updated_refund)
            action_msg = 'approved' if action == 'approve' else 'rejected'
            return Response({
                'success': True,
                'message': f'Refund request has been {action_msg}',
                'data': refund_serializer.data,
            })

        except RefundError as e:
            return Response({
                'success': False,
                'message': str(e),
                'data': None,
            }, status=status.HTTP_400_BAD_REQUEST)


class CompleteRefundView(APIView):
    """
    POST /api/refunds/{id}/complete/
    Admin-only endpoint to complete an approved refund.
    Returns money from receiver back to sender.
    """
    permission_classes = [IsAuthenticated, IsAdminOnly]

    def post(self, request, pk):
        try:
            refund = Refund.objects.get(pk=pk)
        except Refund.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Refund not found',
                'data': None,
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = CompleteRefundSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        admin_note = serializer.validated_data.get('admin_note', '')

        try:
            updated_refund = RefundService.complete_refund(
                refund=refund,
                admin_user=request.user,
                admin_note=admin_note,
            )

            refund_serializer = RefundSerializer(updated_refund)
            return Response({
                'success': True,
                'message': f'Refund of ${refund.amount:.2f} has been completed. Money has been returned.',
                'data': refund_serializer.data,
            })

        except RefundError as e:
            return Response({
                'success': False,
                'message': str(e),
                'data': None,
            }, status=status.HTTP_400_BAD_REQUEST)
