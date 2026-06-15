from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Admin for the Transaction model.
    """

    list_display = [
        'reference_number', 'sender_wallet', 'receiver_wallet',
        'amount', 'fee', 'transaction_type', 'status', 'created_at'
    ]
    list_filter = ['transaction_type', 'status', 'created_at']
    search_fields = [
        'reference_number',
        'sender_wallet__wallet_number',
        'receiver_wallet__wallet_number',
        'sender_wallet__user__username',
        'receiver_wallet__user__username',
    ]
    readonly_fields = ['reference_number', 'created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = (
        (None, {
            'fields': ('reference_number', 'sender_wallet', 'receiver_wallet')
        }),
        ('Amount', {
            'fields': ('amount', 'fee', 'transaction_type', 'status')
        }),
        ('Details', {
            'fields': ('description',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def has_add_permission(self, request):
        return False
