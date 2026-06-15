from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Notification
from .serializers import (
    NotificationSerializer,
    NotificationListSerializer,
    MarkReadSerializer,
    UnreadCountSerializer,
)


class NotificationListView(generics.ListAPIView):
    """
    GET /api/notifications/
    List all notifications for the authenticated user.
    Supports filtering by read status and notification type.
    """
    serializer_class = NotificationListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Notification.objects.filter(
            user=self.request.user
        ).order_by('-created_at')

        # Filter by read status
        is_read = self.request.query_params.get('is_read', None)
        if is_read is not None:
            is_read_bool = is_read.lower() in ('true', '1', 'yes')
            queryset = queryset.filter(is_read=is_read_bool)

        # Filter by notification type
        notification_type = self.request.query_params.get('type', None)
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)

        return queryset


class MarkNotificationReadView(APIView):
    """
    PUT /api/notifications/{id}/read/
    Mark a specific notification as read.
    """
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            notification = Notification.objects.get(
                pk=pk,
                user=request.user
            )
        except Notification.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Notification not found',
                'data': None,
            }, status=status.HTTP_404_NOT_FOUND)

        notification.is_read = True
        notification.save()

        serializer = NotificationSerializer(notification)
        return Response({
            'success': True,
            'message': 'Notification marked as read',
            'data': serializer.data,
        })


class MarkAllNotificationsReadView(APIView):
    """
    PUT /api/notifications/read-all/
    Mark all notifications as read for the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def put(self, request):
        updated_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)

        return Response({
            'success': True,
            'message': f'{updated_count} notification(s) marked as read',
            'data': {
                'updated_count': updated_count,
            }
        })


class UnreadNotificationCountView(APIView):
    """
    GET /api/notifications/unread-count/
    Get the count of unread notifications for the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()

        serializer = UnreadCountSerializer({'unread_count': unread_count})
        return Response({
            'success': True,
            'message': 'Unread count retrieved successfully',
            'data': serializer.data,
        })
