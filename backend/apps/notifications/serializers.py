from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Full serializer for the Notification model.
    """

    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'title', 'message',
            'notification_type', 'is_read', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'title', 'message', 'notification_type', 'created_at']


class NotificationListSerializer(serializers.ModelSerializer):
    """
    Serializer for notification list views.
    """

    time_ago = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'notification_type',
            'is_read', 'created_at', 'time_ago'
        ]
        read_only_fields = fields

    def get_time_ago(self, obj):
        """Return a human-readable time ago string."""
        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()
        diff = now - obj.created_at

        if diff < timedelta(minutes=1):
            return 'Just now'
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f'{minutes} minute{"s" if minutes != 1 else ""} ago'
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f'{hours} hour{"s" if hours != 1 else ""} ago'
        elif diff < timedelta(days=7):
            days = diff.days
            return f'{days} day{"s" if days != 1 else ""} ago'
        else:
            weeks = diff.days // 7
            return f'{weeks} week{"s" if weeks != 1 else ""} ago'


class MarkReadSerializer(serializers.Serializer):
    """
    Serializer for marking a notification as read.
    """

    is_read = serializers.BooleanField(default=True)


class UnreadCountSerializer(serializers.Serializer):
    """
    Serializer for unread notification count.
    """

    unread_count = serializers.IntegerField()
