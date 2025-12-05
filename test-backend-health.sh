#!/bin/bash

# Backend Health Check Script
BACKEND_URL="https://payment-gateway-integration-371z.onrender.com/api"

echo "🏥 Backend Health Check"
echo "======================="
echo ""

echo "Testing health endpoint..."
echo "URL: ${BACKEND_URL}/health/"
echo ""

HEALTH_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "${BACKEND_URL}/health/")

HTTP_CODE=$(echo "$HEALTH_RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
BODY=$(echo "$HEALTH_RESPONSE" | sed '/HTTP_CODE/d')

echo "Response:"
echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
echo ""
echo "HTTP Status: $HTTP_CODE"
echo ""

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Backend is responding!"
    echo ""
    echo "Checking status..."
    
    if echo "$BODY" | grep -q '"status": "ok"'; then
        echo "✅ Status: OK"
    else
        echo "⚠️ Status: ERROR - Check the response above"
    fi
    
    if echo "$BODY" | grep -q '"database": "connected"'; then
        echo "✅ Database: Connected"
    else
        echo "❌ Database: NOT connected - Need to check DATABASE_URL"
    fi
    
    if echo "$BODY" | grep -q '"users_count"'; then
        USER_COUNT=$(echo "$BODY" | grep -o '"users_count": [0-9]*' | grep -o '[0-9]*')
        echo "ℹ️ Users in database: $USER_COUNT"
    fi
else
    echo "❌ Backend is NOT responding correctly"
    echo ""
    echo "Possible issues:"
    echo "1. Service is not running on Render"
    echo "2. Database migrations not run"
    echo "3. Environment variables not set"
    echo "4. Check Render logs for errors"
fi

echo ""
echo "---"
echo ""
echo "Next: Check Render logs at:"
echo "https://dashboard.render.com → Your Service → Logs"
