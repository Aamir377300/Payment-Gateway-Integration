import hashlib
import hmac
import uuid
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum

from .models import PaymentLog, Transaction

MIN_AMOUNT = Decimal('1.00')
MAX_AMOUNT = Decimal('100000.00')
PAGE_SIZE = 8
DEMO_EMAIL = 'demo@paygate.dev'
DEMO_PASSWORD = 'DemoPass123'


class PaymentError(Exception):
    def __init__(self, message, status=400):
        self.message = message
        self.status = status
        super().__init__(message)


def payment_mode():
    """sandbox or razorpay. auto uses Razorpay as soon as both keys are set."""
    mode = getattr(settings, 'PAYMENT_MODE', 'auto')
    has_keys = bool(settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET)
    if mode == 'sandbox':
        return 'sandbox'
    if mode == 'razorpay':
        if not has_keys:
            raise PaymentError('Razorpay keys are not configured.', 500)
        return 'razorpay'
    return 'razorpay' if has_keys else 'sandbox'


def key_kind():
    key_id = settings.RAZORPAY_KEY_ID or ''
    if key_id.startswith('rzp_live_'):
        return 'live'
    if key_id.startswith('rzp_test_'):
        return 'test'
    if key_id:
        return 'unknown'
    return 'none'


def charge_mode():
    """What a checkout will actually do: sandbox, Razorpay test, or a real charge."""
    if payment_mode() != 'razorpay':
        return 'sandbox'
    return 'live' if key_kind() == 'live' else 'test'


def signing_secret():
    if payment_mode() == 'sandbox':
        return settings.DEMO_SIGNING_SECRET
    return settings.RAZORPAY_KEY_SECRET


def webhook_secret():
    if payment_mode() != 'razorpay':
        return settings.DEMO_SIGNING_SECRET
    return settings.RAZORPAY_WEBHOOK_SECRET or settings.RAZORPAY_KEY_SECRET


def safe_compare(left, right):
    if not isinstance(left, str) or not isinstance(right, str):
        return False
    if len(left) != len(right):
        return False
    return hmac.compare_digest(left, right)


def make_signature(order_id, payment_id):
    return hmac.new(
        signing_secret().encode(),
        f'{order_id}|{payment_id}'.encode(),
        hashlib.sha256,
    ).hexdigest()


def sign_webhook(body):
    if isinstance(body, str):
        body = body.encode()
    return hmac.new(webhook_secret().encode(), body, hashlib.sha256).hexdigest()


def get_client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def parse_amount(raw):
    if raw is None or str(raw).strip() == '':
        raise PaymentError('Amount is required.')
    try:
        amount = Decimal(str(raw))
    except (InvalidOperation, ValueError):
        raise PaymentError('Enter a valid amount.')
    if amount.as_tuple().exponent < -2:
        raise PaymentError('Use at most 2 decimal places.')
    amount = amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    if amount < MIN_AMOUNT:
        raise PaymentError('Amount must be at least 1.00.')
    if amount > MAX_AMOUNT:
        raise PaymentError('Amount cannot exceed 100000.00.')
    return amount


def clean_description(raw):
    description = (raw or '').strip()
    if not description:
        raise PaymentError('Description is required.')
    if len(description) > 200:
        raise PaymentError('Description must be 200 characters or fewer.')
    return description


def serialize_transaction(transaction):
    return {
        'id': transaction.id,
        'order_id': transaction.order_id,
        'razorpay_order_id': transaction.razorpay_order_id,
        'razorpay_payment_id': transaction.razorpay_payment_id,
        'amount': f'{transaction.amount:.2f}',
        'currency': transaction.currency,
        'description': transaction.description,
        'status': transaction.status,
        'provider': transaction.provider,
        'failure_reason': transaction.failure_reason,
        'created_at': transaction.created_at.isoformat(),
        'updated_at': transaction.updated_at.isoformat(),
    }


def serialize_activity(log):
    return {
        'event_type': log.event_type,
        'message': log.message,
        'created_at': log.created_at.isoformat(),
    }


def log_event(transaction, event_type, message, ip_address, payload=None):
    return PaymentLog.objects.create(
        transaction=transaction,
        event_type=event_type,
        payload=payload,
        message=message,
        ip_address=ip_address,
    )


def display_name(user):
    full_name = user.get_full_name().strip()
    if full_name:
        return full_name
    if user.email:
        return user.email.split('@')[0]
    return user.username


def create_order(user, amount_raw, description_raw, ip_address):
    amount = parse_amount(amount_raw)
    description = clean_description(description_raw)
    mode = payment_mode()
    order_id = f'ORD-{user.id}-{uuid.uuid4().hex[:10].upper()}'

    transaction = Transaction.objects.create(
        user=user,
        order_id=order_id,
        amount=amount,
        currency='INR',
        description=description,
        status='PENDING',
        provider=mode,
        receipt=order_id,
    )

    if mode == 'sandbox':
        transaction.razorpay_order_id = f'order_demo_{uuid.uuid4().hex[:14]}'
        transaction.save(update_fields=['razorpay_order_id', 'updated_at'])
        log_event(
            transaction,
            'ORDER_CREATED',
            'Sandbox order created',
            ip_address,
            {'provider': 'sandbox', 'order_id': transaction.razorpay_order_id},
        )
        return transaction

    import razorpay

    try:
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create({
            'amount': int(amount * 100),
            'currency': 'INR',
            'receipt': transaction.order_id,
        })
    except Exception:
        transaction.status = 'FAILED'
        transaction.failure_reason = 'The payment provider could not create this order.'
        transaction.save(update_fields=['status', 'failure_reason', 'updated_at'])
        log_event(transaction, 'PAYMENT_FAILED', transaction.failure_reason, ip_address)
        raise PaymentError('Could not create the payment order. Check the Razorpay keys.', 502)

    transaction.razorpay_order_id = razorpay_order['id']
    transaction.receipt = razorpay_order.get('receipt') or order_id
    transaction.save(update_fields=['razorpay_order_id', 'receipt', 'updated_at'])
    log_event(
        transaction,
        'ORDER_CREATED',
        f"Order created: {razorpay_order['id']}",
        ip_address,
        {'id': razorpay_order.get('id'), 'amount': razorpay_order.get('amount')},
    )
    return transaction


def order_payload(transaction, user):
    mode = transaction.provider
    return {
        'transaction': serialize_transaction(transaction),
        'payment_mode': mode,
        'charge_mode': 'sandbox' if mode == 'sandbox' else charge_mode(),
        'razorpay_key_id': settings.RAZORPAY_KEY_ID if mode == 'razorpay' else '',
        'razorpay_order_id': transaction.razorpay_order_id,
        'amount': f'{transaction.amount:.2f}',
        'amount_in_paise': int(transaction.amount * 100),
        'currency': transaction.currency,
        'description': transaction.description,
        'user_name': display_name(user),
        'user_email': user.email,
    }


def owned_transaction(user, **lookup):
    try:
        return Transaction.objects.get(user=user, **lookup)
    except Transaction.DoesNotExist:
        raise PaymentError('Transaction not found.', 404)


def verify_payment(user, order_id, payment_id, signature, ip_address):
    if not order_id or not payment_id or not signature:
        raise PaymentError('Payment confirmation is incomplete.')

    transaction = owned_transaction(user, razorpay_order_id=order_id)

    if transaction.status == 'SUCCESS' and transaction.razorpay_payment_id == payment_id:
        return transaction

    if transaction.status != 'PENDING':
        raise PaymentError('This payment can no longer be confirmed.', 409)

    if not safe_compare(make_signature(order_id, payment_id), signature):
        transaction.status = 'FAILED'
        transaction.failure_reason = 'Payment signature did not match.'
        transaction.save(update_fields=['status', 'failure_reason', 'updated_at'])
        log_event(transaction, 'SIGNATURE_FAILED', transaction.failure_reason, ip_address)
        raise PaymentError('Payment verification failed.')

    transaction.razorpay_payment_id = payment_id
    transaction.razorpay_signature = signature
    transaction.status = 'SUCCESS'
    transaction.failure_reason = ''
    transaction.save(update_fields=[
        'razorpay_payment_id', 'razorpay_signature', 'status', 'failure_reason', 'updated_at'
    ])
    log_event(
        transaction,
        'PAYMENT_SUCCESS',
        'Payment verified',
        ip_address,
        {'order_id': order_id, 'payment_id': payment_id},
    )
    log_event(transaction, 'SIGNATURE_VERIFIED', 'Signature matched', ip_address)
    return transaction


def mark_failed(user, transaction_id, reason, ip_address):
    transaction = owned_transaction(user, id=transaction_id)
    if transaction.status != 'PENDING':
        return transaction

    transaction.status = 'FAILED'
    transaction.failure_reason = (reason or 'Payment was cancelled.')[:255]
    transaction.save(update_fields=['status', 'failure_reason', 'updated_at'])
    log_event(transaction, 'PAYMENT_FAILED', transaction.failure_reason, ip_address)
    return transaction


def complete_sandbox(user, transaction_id, outcome, ip_address):
    transaction = owned_transaction(user, id=transaction_id)
    if transaction.provider != 'sandbox':
        raise PaymentError('Sandbox completion is only available for sandbox orders.')
    if transaction.status != 'PENDING':
        raise PaymentError('This payment can no longer be changed.', 409)

    if outcome == 'success':
        payment_id = f'pay_demo_{uuid.uuid4().hex[:14]}'
        signature = make_signature(transaction.razorpay_order_id, payment_id)
        return verify_payment(user, transaction.razorpay_order_id, payment_id, signature, ip_address)

    if outcome == 'failed':
        return mark_failed(user, transaction.id, 'Card was declined in the sandbox.', ip_address)

    raise PaymentError('Choose a success or failed outcome.')


def refund_transaction(user, transaction_id, ip_address):
    transaction = owned_transaction(user, id=transaction_id)
    if transaction.status != 'SUCCESS':
        raise PaymentError('Only a successful payment can be refunded.')

    if transaction.provider == 'razorpay':
        import razorpay
        try:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            client.payment.refund(transaction.razorpay_payment_id, {
                'amount': int(transaction.amount * 100),
            })
        except Exception:
            raise PaymentError('The payment provider rejected the refund.', 502)

    transaction.status = 'REFUNDED'
    transaction.save(update_fields=['status', 'updated_at'])
    log_event(
        transaction,
        'REFUND',
        'Payment refunded',
        ip_address,
        {'amount': f'{transaction.amount:.2f}'},
    )
    return transaction


def filtered_transactions(user, status='', query=''):
    transactions = Transaction.objects.filter(user=user)
    if status in dict(Transaction.STATUS):
        transactions = transactions.filter(status=status)
    query = (query or '').strip()[:100]
    if query:
        transactions = transactions.filter(
            Q(order_id__icontains=query)
            | Q(description__icontains=query)
            | Q(razorpay_payment_id__icontains=query)
        )
    return transactions


def paginate_transactions(user, status='', query='', page=1):
    try:
        page_number = max(int(page), 1)
    except (TypeError, ValueError):
        page_number = 1

    paginator = Paginator(filtered_transactions(user, status, query), PAGE_SIZE)
    current = paginator.get_page(page_number)
    return {
        'count': paginator.count,
        'page': current.number,
        'page_size': PAGE_SIZE,
        'num_pages': paginator.num_pages,
        'results': [serialize_transaction(item) for item in current.object_list],
    }


def summary_for(user):
    rows = Transaction.objects.filter(user=user).values('status').annotate(
        count=Count('id'),
        total=Sum('amount'),
    )
    by_status = {row['status']: row for row in rows}

    def count_for(status):
        return by_status.get(status, {}).get('count', 0)

    def amount_for(status):
        total = by_status.get(status, {}).get('total') or Decimal('0')
        return f'{total:.2f}'

    return {
        'total_count': sum(row['count'] for row in rows),
        'successful_count': count_for('SUCCESS'),
        'pending_count': count_for('PENDING'),
        'failed_count': count_for('FAILED'),
        'refunded_count': count_for('REFUNDED'),
        'collected_amount': amount_for('SUCCESS'),
        'refunded_amount': amount_for('REFUNDED'),
        'payment_mode': payment_mode(),
    }


def apply_webhook(payload):
    event = payload.get('event')
    payment = (
        payload.get('payload', {})
        .get('payment', {})
        .get('entity', {})
    )
    order_id = payment.get('order_id')
    payment_id = payment.get('id')
    if event not in ('payment.captured', 'payment.failed') or not order_id:
        return 'ignored'

    try:
        transaction = Transaction.objects.get(razorpay_order_id=order_id)
    except Transaction.DoesNotExist:
        return 'ignored'

    if event == 'payment.captured':
        if transaction.status == 'SUCCESS':
            return 'already_processed'
        if transaction.status != 'PENDING' or not payment_id:
            return 'ignored'
        transaction.razorpay_payment_id = payment_id
        transaction.status = 'SUCCESS'
        transaction.failure_reason = ''
        transaction.save(update_fields=['razorpay_payment_id', 'status', 'failure_reason', 'updated_at'])
        log_event(transaction, 'WEBHOOK_RECEIVED', 'payment.captured', None, {'payment_id': payment_id})
        log_event(transaction, 'PAYMENT_SUCCESS', 'Payment captured by webhook', None)
        return 'processed'

    if transaction.status == 'PENDING':
        transaction.status = 'FAILED'
        transaction.failure_reason = 'The provider reported a failed payment.'
        transaction.save(update_fields=['status', 'failure_reason', 'updated_at'])
        log_event(transaction, 'WEBHOOK_RECEIVED', 'payment.failed', None)
        log_event(transaction, 'PAYMENT_FAILED', transaction.failure_reason, None)
        return 'processed'
    return 'ignored'
