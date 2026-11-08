from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone

from .models import PaymentLog, Transaction
from .services import DEMO_EMAIL, DEMO_PASSWORD, payment_mode


SAMPLES = [
    {
        'description': 'Brand identity retainer',
        'amount': Decimal('2499.00'),
        'status': 'SUCCESS',
        'days_ago': 12,
        'payment': True,
    },
    {
        'description': 'Workshop seat — Friday cohort',
        'amount': Decimal('1299.00'),
        'status': 'SUCCESS',
        'days_ago': 6,
        'payment': True,
    },
    {
        'description': 'Domain renewal',
        'amount': Decimal('899.00'),
        'status': 'REFUNDED',
        'days_ago': 3,
        'payment': True,
    },
    {
        'description': 'Print run deposit',
        'amount': Decimal('4500.00'),
        'status': 'PENDING',
        'days_ago': 1,
        'payment': False,
    },
    {
        'description': 'Stock photo license',
        'amount': Decimal('499.00'),
        'status': 'FAILED',
        'days_ago': 2,
        'payment': False,
        'failure_reason': 'Card was declined in the sandbox.',
    },
]


def seed_demo_user(force=False):
    if not force:
        if settings.TESTING or getattr(settings, 'SEED_DEMO', '') == '0':
            return None
        try:
            mode = payment_mode()
        except Exception:
            mode = 'razorpay'
        if not settings.DEBUG and mode != 'sandbox':
            return None

    user, created = User.objects.get_or_create(
        username=DEMO_EMAIL,
        defaults={
            'email': DEMO_EMAIL,
            'first_name': 'Demo',
            'last_name': 'Merchant',
        },
    )
    if created:
        user.email = DEMO_EMAIL
        user.set_password(DEMO_PASSWORD)
        user.save()

    if Transaction.objects.filter(user=user).exists():
        return user

    now = timezone.now()
    for index, sample in enumerate(SAMPLES, start=1):
        paid = sample['payment']
        transaction = Transaction.objects.create(
            user=user,
            order_id=f'ORD-DEMO-{index:03d}',
            amount=sample['amount'],
            currency='INR',
            status=sample['status'],
            provider='sandbox',
            description=sample['description'],
            failure_reason=sample.get('failure_reason', ''),
            razorpay_order_id=f'order_demo_seed_{index:03d}',
            razorpay_payment_id=f'pay_demo_seed_{index:03d}' if paid else '',
            receipt=f'ORD-DEMO-{index:03d}',
        )
        when = now - timedelta(days=sample['days_ago'])
        Transaction.objects.filter(pk=transaction.pk).update(created_at=when, updated_at=when)
        PaymentLog.objects.create(
            transaction=transaction,
            event_type='ORDER_CREATED',
            message='Seeded sample order',
        )
        if sample['status'] == 'SUCCESS':
            PaymentLog.objects.create(
                transaction=transaction,
                event_type='PAYMENT_SUCCESS',
                message='Seeded successful payment',
            )
        elif sample['status'] == 'REFUNDED':
            PaymentLog.objects.create(
                transaction=transaction,
                event_type='PAYMENT_SUCCESS',
                message='Seeded successful payment',
            )
            PaymentLog.objects.create(
                transaction=transaction,
                event_type='REFUND',
                message='Seeded refund',
            )
        elif sample['status'] == 'FAILED':
            PaymentLog.objects.create(
                transaction=transaction,
                event_type='PAYMENT_FAILED',
                message=sample['failure_reason'],
            )
    return user
