from django.db import models
from django.contrib.auth.models import User


class Transaction(models.Model):
    """Model to store payment transaction details"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    order_id = models.CharField(max_length=100, unique=True, db_index=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Razorpay specific fields
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    
    # Additional info
    description = models.TextField(blank=True, null=True)
    receipt = models.CharField(max_length=100, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'transactions'
        ordering = ['-created_at']
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
    
    def __str__(self):
        return f"{self.order_id} - {self.user.email} - {self.status}"


class PaymentLog(models.Model):
    """Model to log webhook events and payment activities"""
    
    EVENT_TYPES = [
        ('ORDER_CREATED', 'Order Created'),
        ('PAYMENT_SUCCESS', 'Payment Success'),
        ('PAYMENT_FAILED', 'Payment Failed'),
        ('WEBHOOK_RECEIVED', 'Webhook Received'),
        ('SIGNATURE_VERIFIED', 'Signature Verified'),
        ('SIGNATURE_FAILED', 'Signature Failed'),
    ]
    
    transaction = models.ForeignKey(
        Transaction, 
        on_delete=models.CASCADE, 
        related_name='logs',
        null=True,
        blank=True
    )
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    payload = models.JSONField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'payment_logs'
        ordering = ['-created_at']
        verbose_name = 'Payment Log'
        verbose_name_plural = 'Payment Logs'
    
    def __str__(self):
        return f"{self.event_type} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
