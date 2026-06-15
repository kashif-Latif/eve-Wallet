from django.urls import path

from .views import (
    RequestRefundView,
    MyRefundsListView,
    RefundListView,
    ProcessRefundView,
    CompleteRefundView,
)

app_name = 'refunds'

urlpatterns = [
    # User endpoints
    path('request/', RequestRefundView.as_view(), name='request_refund'),
    path('my-refunds/', MyRefundsListView.as_view(), name='my_refunds'),

    # Admin endpoints
    path('', RefundListView.as_view(), name='refund_list'),
    path('<int:pk>/process/', ProcessRefundView.as_view(), name='process_refund'),
    path('<int:pk>/complete/', CompleteRefundView.as_view(), name='complete_refund'),
]
