from django.conf import settings

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Transaction, PaymentLog
import razorpay
import hmac
import hashlib
from decimal import Decimal, InvalidOperation


def get_razorpay_client():
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')


def serialize_transaction(transaction):
    return {
        'id': transaction.id,
        'order_id': transaction.order_id,
        'razorpay_order_id': transaction.razorpay_order_id,
        'razorpay_payment_id': transaction.razorpay_payment_id,
        'amount': str(transaction.amount),
        'currency': transaction.currency,
        'description': transaction.description,
        'status': transaction.status,
        'created_at': transaction.created_at.isoformat(),
        'updated_at': transaction.updated_at.isoformat()
    }


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order_api(request):
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"💳 Create order request from: {request.user.username}")
    logger.info(f"   Origin: {request.META.get('HTTP_ORIGIN', 'None')}")
    logger.info(f"   Session Key: {request.session.session_key}")
    
    amount_str = request.data.get('amount')
    description = request.data.get('description', 'Payment')
    
    if not amount_str:
        return Response({'amount': ['This field is required.']}, status=400)
    
    try:
        amount = Decimal(str(amount_str))
        if amount < 1:
            return Response({'amount': ['Amount must be at least 1.']}, status=400)
    except (InvalidOperation, ValueError):
        return Response({'amount': ['Enter a valid number.']}, status=400)
    
    try:
        if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
            logger.error(f"   ❌ Razorpay keys not configured!")
            return Response({'error': 'Razorpay keys not configured.'}, status=500)
        
        amount_in_paise = int(amount * 100)
        logger.info(f"   Amount: ₹{amount} ({amount_in_paise} paise)")
        
        transaction = Transaction.objects.create(
            user=request.user,
            order_id=f"ORD_{request.user.id}_{Transaction.objects.count() + 1}",
            amount=amount,
            currency='INR',
            description=description,
            status='PENDING'
        )
        logger.info(f"   Transaction created: {transaction.order_id}")
        
        client = get_razorpay_client()
        razorpay_order = client.order.create({
            'amount': amount_in_paise,
            'currency': 'INR',
            'receipt': transaction.order_id,
            'payment_capture': 1
        })
        logger.info(f"   Razorpay order created: {razorpay_order['id']}")
        
        transaction.razorpay_order_id = razorpay_order['id']
        transaction.receipt = razorpay_order['receipt']
        transaction.save()
        
        PaymentLog.objects.create(
            transaction=transaction,
            event_type='ORDER_CREATED',
            payload=razorpay_order,
            message=f"Order created: {razorpay_order['id']}",
            ip_address=get_client_ip(request)
        )
        
        user_name = request.user.get_full_name() or request.user.username or request.user.email.split('@')[0]
        
        logger.info(f"   ✅ Order creation successful")
        
        return Response({
            'transaction': serialize_transaction(transaction),
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'razorpay_order_id': razorpay_order['id'],
            'amount': str(amount),
            'amount_in_paise': amount_in_paise,
            'currency': 'INR',
            'description': description,
            'user_name': user_name,
            'user_email': request.user.email,
        })
        
    except razorpay.errors.BadRequestError as e:
        logger.error(f"   ❌ Razorpay authentication failed: {str(e)}")
        return Response({'error': 'Authentication failed. Check Razorpay credentials.'}, status=500)
    except Exception as e:
        logger.error(f"   ❌ Error creating order: {str(e)}")
        logger.exception("Full traceback:")
        return Response({'error': f'Error creating order: {str(e)}'}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_payment_api(request):
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"✅ Verify payment request from: {request.user.username}")
    logger.info(f"   Origin: {request.META.get('HTTP_ORIGIN', 'None')}")
    
    try:
        razorpay_order_id = request.data.get('razorpay_order_id')
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_signature = request.data.get('razorpay_signature')
        
        logger.info(f"   Order ID: {razorpay_order_id}")
        logger.info(f"   Payment ID: {razorpay_payment_id}")
        
        transaction = Transaction.objects.get(razorpay_order_id=razorpay_order_id, user=request.user)
        
        generated_signature = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode(),
            f"{razorpay_order_id}|{razorpay_payment_id}".encode(),
            hashlib.sha256
        ).hexdigest()
        
        if generated_signature == razorpay_signature:
            logger.info(f"   ✅ Signature verified successfully")
            transaction.razorpay_payment_id = razorpay_payment_id
            transaction.razorpay_signature = razorpay_signature
            transaction.status = 'SUCCESS'
            transaction.save()
            
            PaymentLog.objects.create(
                transaction=transaction,
                event_type='PAYMENT_SUCCESS',
                payload={
                    'order_id': razorpay_order_id,
                    'payment_id': razorpay_payment_id,
                    'signature': razorpay_signature
                },
                message='Payment verified successfully',
                ip_address=get_client_ip(request)
            )
            
            return Response({
                'message': 'Payment successful.',
                'transaction': serialize_transaction(transaction)
            })
        else:
            logger.warning(f"   ❌ Signature verification failed")
            transaction.status = 'FAILED'
            transaction.save()
            
            PaymentLog.objects.create(
                transaction=transaction,
                event_type='SIGNATURE_FAILED',
                message='Signature verification failed',
                ip_address=get_client_ip(request)
            )
            
            return Response({'error': 'Payment verification failed.'}, status=400)
            
    except Transaction.DoesNotExist:
        logger.error(f"   ❌ Transaction not found: {razorpay_order_id}")
        return Response({'error': 'Transaction not found.'}, status=404)
    except Exception as e:
        logger.error(f"   ❌ Error verifying payment: {str(e)}")
        return Response({'error': f'Error verifying payment: {str(e)}'}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def payment_failure_api(request):
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"❌ Payment failure request from: {request.user.username}")
    logger.info(f"   Origin: {request.META.get('HTTP_ORIGIN', 'None')}")
    
    try:
        transaction_id = request.data.get('transaction_id')
        logger.info(f"   Transaction ID: {transaction_id}")
        
        transaction = Transaction.objects.get(id=transaction_id, user=request.user)
        
        if transaction.status == 'PENDING':
            transaction.status = 'FAILED'
            transaction.save()
            logger.info(f"   Transaction marked as FAILED")
            
            PaymentLog.objects.create(
                transaction=transaction,
                event_type='PAYMENT_FAILED',
                message='Payment failed or cancelled',
                ip_address=get_client_ip(request)
            )
        
        return Response({
            'message': 'Payment marked as failed.',
            'transaction': serialize_transaction(transaction)
        })
    except Transaction.DoesNotExist:
        logger.error(f"   ❌ Transaction not found: {transaction_id}")
        return Response({'error': 'Transaction not found.'}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_history_api(request):
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"📜 Transaction history request from: {request.user.username}")
    logger.info(f"   Origin: {request.META.get('HTTP_ORIGIN', 'None')}")
    logger.info(f"   Session Key: {request.session.session_key}")
    
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    logger.info(f"   Found {transactions.count()} transactions")
    
    return Response([serialize_transaction(t) for t in transactions])


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_detail_api(request, transaction_id):
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"🔍 Transaction detail request: {transaction_id} from {request.user.username}")
    logger.info(f"   Origin: {request.META.get('HTTP_ORIGIN', 'None')}")
    
    try:
        transaction = Transaction.objects.get(id=transaction_id, user=request.user)
        logger.info(f"   ✅ Transaction found: {transaction.order_id}")
        return Response(serialize_transaction(transaction))
    except Transaction.DoesNotExist:
        logger.error(f"   ❌ Transaction not found: {transaction_id}")
        return Response({'error': 'Transaction not found.'}, status=404)
