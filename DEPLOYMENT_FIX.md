# Deployment Fix for 403 Forbidden Error

## Problem
Getting 403 Forbidden when accessing `/api/auth/user/` after CSRF token fetch. This happens because of cookie handling issues in cross-origin deployments (Render backend + Vercel frontend).

## Root Causes
1. **SameSite=None cookies require Secure=True** - Session cookies won't work across domains without proper configuration
2. **CORS headers not fully configured** - Missing some required headers for cross-origin requests
3. **Frontend .env pointing to localhost** - Not using production backend URL

## Fixes Applied

### Backend (Django on Render)

#### 1. Updated `settings.py` - Cookie Configuration
```python
# CSRF cookies must use SameSite=None and Secure=True for cross-origin
CSRF_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_DOMAIN = None  # Let browser handle it

# Session cookies same configuration
SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_DOMAIN = None
```

#### 2. Added CORS Headers
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

#### 3. Added Your Vercel Domain
Added `https://payment-gateway-integration-ashen.vercel.app` to:
- `CORS_ALLOWED_ORIGINS`
- `CSRF_TRUSTED_ORIGINS`

### Frontend (React on Vercel)

#### 1. Updated `.env` and created `.env.production`
```
VITE_API_URL=https://payment-gateway-integration-371z.onrender.com/api
```

#### 2. Enhanced Axios Interceptor
Added automatic CSRF token retry on 403 errors.

## Deployment Steps

### Backend (Render)

1. **Update Environment Variables on Render:**
   ```
   DEBUG=False
   FRONTEND_URI=https://payment-gateway-integration-ashen.vercel.app
   SECRET_KEY=<your-secret-key>
   DATABASE_URL=<auto-set-by-render>
   RAZORPAY_KEY_ID=<your-key>
   RAZORPAY_KEY_SECRET=<your-secret>
   ```

2. **Commit and push changes:**
   ```bash
   cd payment_gateway
   git add .
   git commit -m "Fix CORS and cookie configuration for production"
   git push
   ```

3. **Render will auto-deploy** - Wait for deployment to complete

### Frontend (Vercel)

1. **Update Environment Variables on Vercel:**
   - Go to your Vercel project settings
   - Add environment variable:
     ```
     VITE_API_URL=https://payment-gateway-integration-371z.onrender.com/api
     ```

2. **Redeploy:**
   ```bash
   cd frontend
   git add .
   git commit -m "Update API URL for production"
   git push
   ```

3. **Or trigger manual redeploy** from Vercel dashboard

## Testing After Deployment

1. Open browser DevTools (Network tab)
2. Visit your Vercel app
3. Check the `/csrf/` request - should return 200
4. Check the `/auth/user/` request - should return 200 (if logged in) or 401 (if not logged in)
5. Look for cookies in Application tab - you should see `csrftoken` and `sessionid` with:
   - `SameSite: None`
   - `Secure: ✓`

## Common Issues

### Issue: Still getting 403
**Solution:** Clear browser cookies and cache, then try again.

### Issue: Cookies not being set
**Solution:** Ensure both backend and frontend are using HTTPS (not HTTP).

### Issue: CORS errors
**Solution:** Double-check that your Vercel domain is in both `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS`.

### Issue: Session not persisting
**Solution:** Verify `withCredentials: true` is set in axios config.

## Verification Checklist

- [ ] Backend deployed on Render with updated settings
- [ ] Frontend deployed on Vercel with correct API URL
- [ ] Environment variables set correctly on both platforms
- [ ] HTTPS enabled on both domains
- [ ] CSRF token fetches successfully (200 response)
- [ ] User authentication works (login/logout)
- [ ] Cookies visible in browser with correct flags
- [ ] No CORS errors in console

## Additional Notes

- **Local Development:** Uses `SameSite=Lax` and `Secure=False` (when DEBUG=True)
- **Production:** Uses `SameSite=None` and `Secure=True` (always)
- **Cookie Domain:** Set to `None` to let the browser handle it automatically
