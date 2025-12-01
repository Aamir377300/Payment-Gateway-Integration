#!/usr/bin/env python
"""
Verify Razorpay keys are valid by making a test API call
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'payment_gateway.settings')
django.setup()

from django.conf import settings
import razorpay

print("\n" + "="*70)
print("🔐 RAZORPAY KEY VERIFICATION")
print("="*70)

# Step 1: Check if keys exist
print("\n1️⃣ Checking if keys are loaded from .env...")
print(f"   KEY_ID: {settings.RAZORPAY_KEY_ID}")
print(f"   KEY_SECRET: {settings.RAZORPAY_KEY_SECRET[:15]}..." if len(settings.RAZORPAY_KEY_SECRET) > 15 else f"   KEY_SECRET: {settings.RAZORPAY_KEY_SECRET}")

if not settings.RAZORPAY_KEY_ID:
    print("\nERROR: RAZORPAY_KEY_ID is empty!")
    print("   Please add your key to payment_gateway/.env")
    sys.exit(1)

if not settings.RAZORPAY_KEY_SECRET:
    print("\nERROR: RAZORPAY_KEY_SECRET is empty!")
    print("   Please add your secret to payment_gateway/.env")
    sys.exit(1)

print("   Keys are loaded")

# Step 2: Check key format
print("\n2️⃣ Checking key format...")
if not settings.RAZORPAY_KEY_ID.startswith('rzp_'):
    print(f"   ⚠️  WARNING: Key ID doesn't start with 'rzp_'")
    print(f"   Your key: {settings.RAZORPAY_KEY_ID}")
    print(f"   Expected format: rzp_test_XXXX or rzp_live_XXXX")

if settings.RAZORPAY_KEY_ID.startswith('rzp_test_'):
    print("   Using TEST mode keys (sandbox)")
elif settings.RAZORPAY_KEY_ID.startswith('rzp_live_'):
    print("   ⚠️  Using LIVE mode keys (real money!)")
else:
    print("   ⚠️  Unknown key format")

# Step 3: Try to initialize client
print("\n3️⃣ Initializing Razorpay client...")
try:
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    print("   Client initialized")
except Exception as e:
    print(f"   Failed to initialize: {e}")
    sys.exit(1)

# Step 4: Try to create a test order
print("\n4️⃣ Testing API connection with test order...")
try:
    test_order = client.order.create({
        'amount': 10000,  # ₹100
        'currency': 'INR',
        'receipt': 'TEST_VERIFICATION',
        'payment_capture': 1
    })
    print("   API call successful!")
    print(f"   Test Order ID: {test_order['id']}")
    print(f"   Amount: ₹{test_order['amount']/100}")
    print(f"   Status: {test_order['status']}")
    
except razorpay.errors.BadRequestError as e:
    print(f"   BAD REQUEST ERROR")
    print(f"   Error: {str(e)}")
    print(f"\n   Possible reasons:")
    print(f"   1. Invalid API keys")
    print(f"   2. Keys are expired")
    print(f"   3. Keys are for wrong mode (test vs live)")
    print(f"   4. Razorpay account not activated")
    print(f"   5. Keys have been regenerated in dashboard")
    print(f"\n   Solution:")
    print(f"   1. Go to https://dashboard.razorpay.com/app/keys")
    print(f"   2. Check if your keys are active")
    print(f"   3. If needed, regenerate keys")
    print(f"   4. Update payment_gateway/.env with new keys")
    sys.exit(1)
    
except razorpay.errors.ServerError as e:
    print(f"   SERVER ERROR")
    print(f"   Error: {str(e)}")
    print(f"   Razorpay API might be down. Try again later.")
    sys.exit(1)
    
except Exception as e:
    print(f"   UNEXPECTED ERROR")
    print(f"   Error type: {type(e).__name__}")
    print(f"   Error: {str(e)}")
    import traceback
    print(f"\n   Full traceback:")
    print(traceback.format_exc())
    sys.exit(1)

# Step 5: Summary
print("\n" + "="*70)
print("ALL CHECKS PASSED!")
print("="*70)
print("\nYour Razorpay integration is configured correctly.")
print("You can now:")
print("1. Start the server: python manage.py runserver")
print("2. Make a payment at http://localhost:8000")
print("3. It should work without authentication errors")
print("\n" + "="*70 + "\n")
