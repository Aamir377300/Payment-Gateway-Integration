from django.contrib import admin
from django.utils.html import format_html
from .models import Transaction, PaymentLog


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'user_email', 'amount_display', 'currency', 'status_badge', 'created_at']
    list_filter = ['status', 'currency', 'created_at']
    search_fields = ['order_id', 'razorpay_order_id', 'razorpay_payment_id', 'user__email', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'order_id']
    date_hierarchy = 'created_at'
    list_per_page = 25
    actions = ['mark_as_success', 'mark_as_failed', 'mark_as_refunded']
    
    fieldsets = (
        ('Transaction Info', {
            'fields': ('user', 'order_id', 'amount', 'currency', 'status', 'description')
        }),
        ('Razorpay Details', {
            'fields': ('razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature', 'receipt')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'
    
    def amount_display(self, obj):
        return f"{obj.amount} {obj.currency}"
    amount_display.short_description = 'Amount'
    amount_display.admin_order_field = 'amount'
    
    def status_badge(self, obj):
        colors = {
            'PENDING': '#FFA500',
            'SUCCESS': '#28a745',
            'FAILED': '#dc3545',
            'REFUNDED': '#6c757d',
        }
        color = colors.get(obj.status, '#000')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.status
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    # Admin actions
    def mark_as_success(self, request, queryset):
        updated = queryset.update(status='SUCCESS')
        self.message_user(request, f'{updated} transaction(s) marked as SUCCESS.')
    mark_as_success.short_description = 'Mark selected as SUCCESS'
    
    def mark_as_failed(self, request, queryset):
        updated = queryset.update(status='FAILED')
        self.message_user(request, f'{updated} transaction(s) marked as FAILED.')
    mark_as_failed.short_description = 'Mark selected as FAILED'
    
    def mark_as_refunded(self, request, queryset):
        updated = queryset.update(status='REFUNDED')
        self.message_user(request, f'{updated} transaction(s) marked as REFUNDED.')
    mark_as_refunded.short_description = 'Mark selected as REFUNDED'


@admin.register(PaymentLog)
class PaymentLogAdmin(admin.ModelAdmin):
    list_display = ['event_type_badge', 'transaction_link', 'short_message', 'ip_address', 'created_at']
    list_filter = ['event_type', 'created_at']
    search_fields = ['message', 'transaction__order_id', 'ip_address']
    readonly_fields = ['created_at', 'payload_display']
    date_hierarchy = 'created_at'
    list_per_page = 50
    
    fieldsets = (
        ('Log Info', {
            'fields': ('event_type', 'transaction', 'message', 'ip_address')
        }),
        ('Payload Data', {
            'fields': ('payload_display',),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
    
    def event_type_badge(self, obj):
        colors = {
            'ORDER_CREATED': '#007bff',
            'PAYMENT_SUCCESS': '#28a745',
            'PAYMENT_FAILED': '#dc3545',
            'WEBHOOK_RECEIVED': '#17a2b8',
            'SIGNATURE_VERIFIED': '#28a745',
            'SIGNATURE_FAILED': '#dc3545',
        }
        color = colors.get(obj.event_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.event_type
        )
    event_type_badge.short_description = 'Event Type'
    event_type_badge.admin_order_field = 'event_type'
    
    def transaction_link(self, obj):
        if obj.transaction:
            return format_html(
                '<a href="/admin/payments/transaction/{}/change/">{}</a>',
                obj.transaction.id, obj.transaction.order_id
            )
        return '-'
    transaction_link.short_description = 'Transaction'
    transaction_link.admin_order_field = 'transaction'
    
    def short_message(self, obj):
        if len(obj.message) > 50:
            return obj.message[:50] + '...'
        return obj.message
    short_message.short_description = 'Message'
    
    def payload_display(self, obj):
        if obj.payload:
            import json
            return format_html('<pre>{}</pre>', json.dumps(obj.payload, indent=2))
        return '-'
    payload_display.short_description = 'Payload'
