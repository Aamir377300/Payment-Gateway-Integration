# Quick Fix Summary - 403 Forbidden Error

## What Was Wrong

Your deployment had a **cross-origin cookie issue**. When your frontend (Vercel) tries to talk to your backend (Render), browsers block cookies unless they're configured correctly.

## Key Changes Made

### 1. Backend Settings (`payment_gateway/settings.py`)

**Before:**
```python
CSRF_COOKIE_SAMESITE = 'None' if not DEBUG else 'Lax'
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SAMESITE = 'None' if not DEBUG else 'Lax'
SESSION_COOKIE_SECURE = not DEBUG
```

**After:**
```python
CSRF_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SECURE = True  # Always True for cross-origin
SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = True  # Always True for cross-origin
```

**Why:** Cookies with `SameSite=None` MUST have `Secure=True` to work across domains. The conditional logic was causing issues.

### 2. Added CORS Headers

```python
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
```

**Why:** Ensures all necessary headers are allowed for cross-origin requests.

### 3. Frontend Environment Variables

**Created:** `frontend/.env.production`
```
VITE_API_URL=https://payment-gateway-integration-371z.onrender.com/api
```

**Updated:** `frontend/.env`
```
VITE_API_URL=https://payment-gateway-integration-371z.onrender.com/api
```

**Why:** Your frontend was pointing to localhost instead of your production backend.

### 4. Enhanced Axios Error Handling

Added automatic CSRF token retry on 403 errors in `frontend/src/api/axios.js`.

## What You Need to Do Now

### Step 1: Update Render Environment Variables
```
DEBUG=False
FRONTEND_URI=https://payment-gateway-integration-ashen.vercel.app
```

### Step 2: Commit and Deploy Backend
```bash
cd payment_gateway
git add .
git commit -m "Fix CORS and cookie configuration"
git push
```

### Step 3: Update Vercel Environment Variable
Add in Vercel dashboard:
```
VITE_API_URL=https://payment-gateway-integration-371z.onrender.com/api
```

### Step 4: Deploy Frontend
```bash
cd frontend
git add .
git commit -m "Update API URL for production"
git push
```

### Step 5: Test
1. Clear browser cookies
2. Visit your Vercel app
3. Open DevTools → Network tab
4. Should see successful requests to `/csrf/` and `/auth/user/`

## Debug Tool

Open `frontend/debug-cookies.html` in your browser to test:
- CSRF token fetching
- Cookie visibility
- CORS configuration

## Still Having Issues?

1. **Clear browser cache and cookies completely**
2. **Check browser console for CORS errors**
3. **Verify both sites are using HTTPS** (not HTTP)
4. **Check Render logs** for any backend errors
5. **Use the debug tool** to see what cookies are being set

## Expected Behavior

✅ `/api/csrf/` → 200 OK (sets csrftoken cookie)
✅ `/api/auth/user/` → 401 Unauthorized (if not logged in) or 200 OK (if logged in)
❌ `/api/auth/user/` → 403 Forbidden (this should NOT happen anymore)
