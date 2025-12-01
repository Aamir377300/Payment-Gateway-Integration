from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.contrib import messages
from .models import Transaction, PaymentLog
import razorpay
import hmac
import hashlib
import json
from decimal import Decimal


def get_razorpay_client():
    """Get Razorpay client with current settings"""
    print(f"   🔧 get_razorpay_client() called")
    print(f"   🔑 Using KEY_ID: {settings.RAZORPAY_KEY_ID}")
    print(f"   🔑 Using KEY_SECRET: {settings.RAZORPAY_KEY_SECRET[:10]}...")
    
    try:
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        print(f"   Client created successfully")
        return client
    except Exception as e:
        print(f"   Failed to create client: {e}")
        raise


def get_client_ip(request):
    """Helper function to get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@login_required
def create_order_view(request):
    """Display payment form and create Razorpay order"""
    
    print("\n" + "="*60)
    print("CREATE_ORDER_VIEW CALLED")
    print("="*60)
    
    if request.method == 'POST':
        print("POST request received")
        try:
            # Debug: Print settings to verify keys are loaded
            print(f"\n1️⃣ Checking Razorpay credentials...")
            print(f"   KEY_ID: {settings.RAZORPAY_KEY_ID}")
            print(f"   KEY_SECRET: {settings.RAZORPAY_KEY_SECRET[:10]}..." if settings.RAZORPAY_KEY_SECRET else "   KEY_SECRET: EMPTY!")
            
            if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
                print("   ERROR: Razorpay keys are empty!")
                messages.error(request, 'Razorpay keys not configured. Please contact administrator.')
                return render(request, 'payments/payment_form.html')
            
            print("   Keys are loaded")
            
            # Get form data
            print(f"\n2️⃣ Getting form data...")
            amount = Decimal(request.POST.get('amount', 0))
            description = request.POST.get('description', 'Payment')
            print(f"   Amount: ₹{amount}")
            print(f"   Description: {description}")
            
            # Validation
            if amount <= 0:
                print("   ERROR: Invalid amount")
                messages.error(request, 'Amount must be greater than zero')
                return render(request, 'payments/payment_form.html')
            
            print("   Amount is valid")
            
            # Convert amount to paise (Razorpay uses smallest currency unit)
            amount_in_paise = int(amount * 100)
            print(f"   Amount in paise: {amount_in_paise}")
            
            # Create order in database first
            print(f"\n3️⃣ Creating transaction in database...")
            transaction = Transaction.objects.create(
                user=request.user,
                order_id=f"ORD_{request.user.id}_{Transaction.objects.count() + 1}",
                amount=amount,
                currency='INR',
                description=description,
                status='PENDING'
            )
            print(f"   Transaction created: {transaction.order_id}")
            
            # Create Razorpay order
            print(f"\n4️⃣ Initializing Razorpay client...")
            client = get_razorpay_client()
            print(f"   Client initialized")
            
            print(f"\n5️⃣ Creating Razorpay order...")
            print(f"   Sending to Razorpay API:")
            print(f"   - Amount: {amount_in_paise} paise")
            print(f"   - Currency: INR")
            print(f"   - Receipt: {transaction.order_id}")
            
            razorpay_order = client.order.create({
                'amount': amount_in_paise,
                'currency': 'INR',
                'receipt': transaction.order_id,
                'payment_capture': 1  # Auto capture payment
            })
            
            print(f"   Razorpay order created successfully!")
            print(f"   Order ID: {razorpay_order['id']}")
            
            # Update transaction with Razorpay order ID
            print(f"\n6️⃣ Updating transaction with Razorpay order ID...")
            transaction.razorpay_order_id = razorpay_order['id']
            transaction.receipt = razorpay_order['receipt']
            transaction.save()
            print(f"   Transaction updated")
            
            # Log the order creation
            print(f"\n7️⃣ Logging order creation...")
            PaymentLog.objects.create(
                transaction=transaction,
                event_type='ORDER_CREATED',
                payload=razorpay_order,
                message=f"Order created successfully: {razorpay_order['id']}",
                ip_address=get_client_ip(request)
            )
            print(f"   Log created")
            
            # Prepare context for checkout page
            print(f"\n8️⃣ Preparing checkout page context...")
            context = {
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                'razorpay_order_id': razorpay_order['id'],
                'amount': amount,
                'amount_in_paise': amount_in_paise,
                'currency': 'INR',
                'description': description,
                'user_name': request.user.get_full_name() or request.user.email,
                'user_email': request.user.email,
                'transaction_id': transaction.id,
            }
            print(f"   Context prepared")
            
            print(f"\nSUCCESS! Rendering checkout page...")
            print("="*60 + "\n")
            return render(request, 'payments/payment_checkout.html', context)
            
        except razorpay.errors.BadRequestError as e:
            print(f"\nRAZORPAY BAD REQUEST ERROR:")
            print(f"   Error: {str(e)}")
            print(f"   This usually means:")
            print(f"   - Invalid API keys")
            print(f"   - Keys are for wrong mode (test vs live)")
            print(f"   - Account not activated")
            import traceback
            print(f"\n   Full traceback:")
            print(traceback.format_exc())
            print("="*60 + "\n")
            
            messages.error(request, f'Authentication failed. Please check Razorpay credentials.')
            return render(request, 'payments/payment_form.html')
            
        except Exception as e:
            # Log the full error for debugging
            print(f"\nUNEXPECTED ERROR:")
            print(f"   Error type: {type(e).__name__}")
            print(f"   Error message: {str(e)}")
            import traceback
            error_details = traceback.format_exc()
            print(f"\n   Full traceback:")
            print(error_details)
            print("="*60 + "\n")
            
            messages.error(request, f'Error creating order: {str(e)}')
            return render(request, 'payments/payment_form.html')
    
    print("GET request - showing payment form")
    print("="*60 + "\n")
    return render(request, 'payments/payment_form.html')


@login_required
def verify_payment_view(request):
    """Verify payment signature after successful payment"""
    
    if request.method == 'POST':
        try:
            # Get payment details from POST request
            razorpay_order_id = request.POST.get('razorpay_order_id')
            razorpay_payment_id = request.POST.get('razorpay_payment_id')
            razorpay_signature = request.POST.get('razorpay_signature')
            
            # Find transaction
            transaction = Transaction.objects.get(razorpay_order_id=razorpay_order_id)
            
            # Verify signature
            generated_signature = hmac.new(
                settings.RAZORPAY_KEY_SECRET.encode(),
                f"{razorpay_order_id}|{razorpay_payment_id}".encode(),
                hashlib.sha256
            ).hexdigest()
            
            if generated_signature == razorpay_signature:
                # Signature verified - update transaction
                transaction.razorpay_payment_id = razorpay_payment_id
                transaction.razorpay_signature = razorpay_signature
                transaction.status = 'SUCCESS'
                transaction.save()
                
                # Log success
                PaymentLog.objects.create(
                    transaction=transaction,
                    event_type='PAYMENT_SUCCESS',
                    payload={
                        'order_id': razorpay_order_id,
                        'payment_id': razorpay_payment_id,
                        'signature': razorpay_signature
                    },
                    message='Payment verified and completed successfully',
                    ip_address=get_client_ip(request)
                )
                
                messages.success(request, 'Payment successful!')
                return redirect('payment_success', transaction_id=transaction.id)
            else:
                # Signature verification failed
                transaction.status = 'FAILED'
                transaction.save()
                
                PaymentLog.objects.create(
                    transaction=transaction,
                    event_type='SIGNATURE_FAILED',
                    message='Signature verification failed',
                    ip_address=get_client_ip(request)
                )
                
                messages.error(request, 'Payment verification failed')
                return redirect('payment_failure', transaction_id=transaction.id)
                
        except Transaction.DoesNotExist:
            messages.error(request, 'Transaction not found')
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f'Error verifying payment: {str(e)}')
            return redirect('dashboard')
    
    return redirect('dashboard')


@login_required
def payment_success_view(request, transaction_id):
    """Display payment success page"""
    try:
        transaction = Transaction.objects.get(id=transaction_id, user=request.user)
        context = {
            'transaction': transaction
        }
        return render(request, 'payments/payment_success.html', context)
    except Transaction.DoesNotExist:
        messages.error(request, 'Transaction not found')
        return redirect('dashboard')


@login_required
def payment_failure_view(request, transaction_id):
    """Display payment failure page"""
    try:
        transaction = Transaction.objects.get(id=transaction_id, user=request.user)
        
        # Update status if not already failed
        if transaction.status == 'PENDING':
            transaction.status = 'FAILED'
            transaction.save()
            
            PaymentLog.objects.create(
                transaction=transaction,
                event_type='PAYMENT_FAILED',
                message='Payment failed or cancelled by user',
                ip_address=get_client_ip(request)
            )
        
        context = {
            'transaction': transaction
        }
        return render(request, 'payments/payment_failure.html', context)
    except Transaction.DoesNotExist:
        messages.error(request, 'Transaction not found')
        return redirect('dashboard')


@csrf_exempt
def webhook_handler(request):
    """Handle Razorpay webhook events"""
    
    if request.method == 'POST':
        try:
            # Get webhook signature from headers
            webhook_signature = request.headers.get('X-Razorpay-Signature')
            webhook_body = request.body
            
            # Verify webhook signature
            expected_signature = hmac.new(
                settings.RAZORPAY_KEY_SECRET.encode(),
                webhook_body,
                hashlib.sha256
            ).hexdigest()
            
            if webhook_signature != expected_signature:
                PaymentLog.objects.create(
                    event_type='SIGNATURE_FAILED',
                    message='Webhook signature verification failed',
                    ip_address=get_client_ip(request)
                )
                return HttpResponse(status=400)
            
            # Parse webhook payload
            payload = json.loads(webhook_body)
            event = payload.get('event')
            
            # Log webhook received
            PaymentLog.objects.create(
                event_type='WEBHOOK_RECEIVED',
                payload=payload,
                message=f'Webhook received: {event}',
                ip_address=get_client_ip(request)
            )
            
            # Handle different webhook events
            if event == 'payment.captured':
                payment_entity = payload['payload']['payment']['entity']
                order_id = payment_entity.get('order_id')
                
                try:
                    transaction = Transaction.objects.get(razorpay_order_id=order_id)
                    transaction.status = 'SUCCESS'
                    transaction.razorpay_payment_id = payment_entity.get('id')
                    transaction.save()
                    
                    PaymentLog.objects.create(
                        transaction=transaction,
                        event_type='PAYMENT_SUCCESS',
                        payload=payment_entity,
                        message='Payment captured via webhook',
                        ip_address=get_client_ip(request)
                    )
                except Transaction.DoesNotExist:
                    pass
            
            elif event == 'payment.failed':
                payment_entity = payload['payload']['payment']['entity']
                order_id = payment_entity.get('order_id')
                
                try:
                    transaction = Transaction.objects.get(razorpay_order_id=order_id)
                    transaction.status = 'FAILED'
                    transaction.save()
                    
                    PaymentLog.objects.create(
                        transaction=transaction,
                        event_type='PAYMENT_FAILED',
                        payload=payment_entity,
                        message='Payment failed via webhook',
                        ip_address=get_client_ip(request)
                    )
                except Transaction.DoesNotExist:
                    pass
            
            return HttpResponse(status=200)
            
        except Exception as e:
            PaymentLog.objects.create(
                event_type='WEBHOOK_RECEIVED',
                message=f'Webhook error: {str(e)}',
                ip_address=get_client_ip(request)
            )
            return HttpResponse(status=500)
    
    return HttpResponse(status=405)


@login_required
def transaction_history_view(request):
    """Display user's transaction history"""
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'transactions': transactions
    }
    return render(request, 'payments/transaction_history.html', context)
