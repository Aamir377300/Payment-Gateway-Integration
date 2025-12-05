#!/bin/bash

# API Testing Script for Payment Gateway
# This script tests the backend API endpoints

BACKEND_URL="https://payment-gateway-integration-371z.onrender.com/api"
FRONTEND_URL="https://payment-gateway-integration-ashen.vercel.app"

echo "🧪 Testing Payment Gateway API"
echo "================================"
echo ""

# Test 1: CSRF Token
echo "1️⃣ Testing CSRF endpoint..."
echo "Request: GET ${BACKEND_URL}/csrf/"
CSRF_RESPONSE=$(curl -i -s -X GET \
  "${BACKEND_URL}/csrf/" \
  -H "Origin: ${FRONTEND_URL}" \
  -H "Accept: application/json")

echo "$CSRF_RESPONSE"
echo ""

if echo "$CSRF_RESPONSE" | grep -q "200 OK"; then
  echo "✅ CSRF endpoint working"
else
  echo "❌ CSRF endpoint failed"
fi
echo ""
echo "---"
echo ""

# Test 2: User endpoint (should return 401 or 403)
echo "2️⃣ Testing User endpoint (without auth)..."
echo "Request: GET ${BACKEND_URL}/auth/user/"
USER_RESPONSE=$(curl -i -s -X GET \
  "${BACKEND_URL}/auth/user/" \
  -H "Origin: ${FRONTEND_URL}" \
  -H "Accept: application/json")

echo "$USER_RESPONSE"
echo ""

if echo "$USER_RESPONSE" | grep -q "401"; then
  echo "✅ User endpoint working (401 Unauthorized - expected)"
elif echo "$USER_RESPONSE" | grep -q "403"; then
  echo "⚠️ User endpoint returning 403 - CORS/CSRF issue"
else
  echo "❓ Unexpected response"
fi
echo ""
echo "---"
echo ""

# Test 3: Check CORS headers
echo "3️⃣ Checking CORS headers..."
CORS_RESPONSE=$(curl -i -s -X OPTIONS \
  "${BACKEND_URL}/auth/user/" \
  -H "Origin: ${FRONTEND_URL}" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: X-CSRFToken")

echo "$CORS_RESPONSE"
echo ""

if echo "$CORS_RESPONSE" | grep -q "Access-Control-Allow-Origin"; then
  echo "✅ CORS headers present"
else
  echo "❌ CORS headers missing"
fi
echo ""
echo "---"
echo ""

echo "🏁 Testing complete!"
echo ""
echo "Next steps:"
echo "1. If CSRF endpoint returns 200 OK → Good!"
echo "2. If User endpoint returns 401 → Good! (means auth is required)"
echo "3. If User endpoint returns 403 → Problem! (CORS/CSRF issue)"
echo "4. Check that CORS headers include your frontend URL"
