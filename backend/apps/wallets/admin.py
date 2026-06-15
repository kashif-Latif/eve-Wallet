from django.contrib import admin
from .models import Wallet


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    """
    Admin for the Wallet model.
    """

    list_display = [
        'wallet_number', 'user', 'balance', 'currency',
        'is_active', 'is_frozen', 'daily_limit', 'monthly_limit', 'created_at'
    ]
    list_filter = ['is_active', 'is_frozen', 'currency', 'created_at']
    search_fields = ['wallet_number', 'user__username', 'user__email', 'user__phone']
    readonly_fields = ['wallet_number', 'created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = (
        (None, {
            'fields': ('user', 'wallet_number', 'balance', 'currency')
        }),
        ('Status', {
            'fields': ('is_active', 'is_frozen')
        }),
        ('Limits', {
            'fields': ('daily_limit', 'monthly_limit')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    actions = ['freeze_wallets', 'unfreeze_wallets']

    @admin.action(description='Freeze selected wallets')
    def freeze_wallets(self, request, queryset):
        updated = queryset.update(is_frozen=True)
        self.message_user(request, f'{updated} wallet(s) frozen successfully.')

    @admin.action(description='Unfreeze selected wallets')
    def unfreeze_wallets(self, request, queryset):
        updated = queryset.update(is_frozen=False)
        self.message_user(request, f'{updated} wallet(s) unfrozen successfully.')
