from django.urls import path

from .views import (
    NotificationListView,
    MarkNotificationReadView,
    MarkAllNotificationsReadView,
    UnreadNotificationCountView,
)

app_name = 'notifications'

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification_list'),
    path('read-all/', MarkAllNotificationsReadView.as_view(), name='mark_all_read'),
    path('unread-count/', UnreadNotificationCountView.as_view(), name='unread_count'),
    path('<int:pk>/read/', MarkNotificationReadView.as_view(), name='mark_read'),
]
