from django.contrib import admin
from .models import Transaction, PaymentLog


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'user', 'amount', 'currency', 'status', 'created_at']
    list_filter = ['status', 'currency', 'created_at']
    search_fields = ['order_id', 'razorpay_order_id', 'razorpay_payment_id', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
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


@admin.register(PaymentLog)
class PaymentLogAdmin(admin.ModelAdmin):
    list_display = ['event_type', 'transaction', 'message', 'ip_address', 'created_at']
    list_filter = ['event_type', 'created_at']
    search_fields = ['message', 'transaction__order_id']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
