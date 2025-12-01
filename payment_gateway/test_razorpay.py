#!/usr/bin/env python
"""
Quick test script to verify Razorpay credentials are working
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'payment_gateway.settings')
django.setup()

from django.conf import settings
import razorpay

print("=" * 60)
print("Testing Razorpay Configuration")
print("=" * 60)

# Check if keys are loaded
print("\n1. Checking environment variables...")
print(f"   RAZORPAY_KEY_ID: {settings.RAZORPAY_KEY_ID[:20]}..." if settings.RAZORPAY_KEY_ID else "   NOT SET")
print(f"   RAZORPAY_KEY_SECRET: {settings.RAZORPAY_KEY_SECRET[:10]}..." if settings.RAZORPAY_KEY_SECRET else "   NOT SET")

if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
    print("\nERROR: Razorpay keys not found in .env file!")
    print("   Please add your keys to payment_gateway/.env")
    exit(1)

# Try to initialize client
print("\n2. Initializing Razorpay client...")
try:
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    print("   Client initialized successfully")
except Exception as e:
    print(f"   Failed to initialize client: {e}")
    exit(1)

# Try to create a test order
print("\n3. Creating test order...")
try:
    order = client.order.create({
        'amount': 10000,  # ₹100 in paise
        'currency': 'INR',
        'receipt': 'TEST_ORDER_001',
        'payment_capture': 1
    })
    print("   Test order created successfully!")
    print(f"   Order ID: {order['id']}")
    print(f"   Amount: ₹{order['amount']/100}")
    print(f"   Currency: {order['currency']}")
    print(f"   Status: {order['status']}")
except Exception as e:
    print(f"   Failed to create order: {e}")
    print("\n   Possible reasons:")
    print("   - Invalid API keys")
    print("   - Keys are for wrong mode (test vs live)")
    print("   - Network connection issue")
    print("   - Razorpay API is down")
    exit(1)

print("\n" + "=" * 60)
print("All tests passed! Razorpay is configured correctly.")
print("=" * 60)
print("\nYou can now:")
print("1. Start the server: python manage.py runserver")
print("2. Go to http://localhost:8000")
print("3. Make a payment and it should work!")
