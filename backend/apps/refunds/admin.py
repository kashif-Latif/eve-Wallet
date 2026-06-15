from django.contrib import admin
from .models import Refund


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    """
    Admin for the Refund model.
    """

    list_display = [
        'id', 'transaction', 'requested_by', 'amount',
        'status', 'processed_by', 'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = [
        'transaction__reference_number',
        'requested_by__username',
        'reason',
    ]
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = (
        (None, {
            'fields': ('transaction', 'requested_by', 'reason', 'amount')
        }),
        ('Status', {
            'fields': ('status', 'admin_note', 'processed_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
