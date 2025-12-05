# Testing Checklist After Deployment

## Pre-Deployment Checks

- [ ] Backend environment variables set on Render
  - [ ] `DEBUG=False`
  - [ ] `FRONTEND_URI=https://payment-gateway-integration-ashen.vercel.app`
  - [ ] `SECRET_KEY` set
  - [ ] `RAZORPAY_KEY_ID` set
  - [ ] `RAZORPAY_KEY_SECRET` set

- [ ] Frontend environment variable set on Vercel
  - [ ] `VITE_API_URL=https://payment-gateway-integration-371z.onrender.com/api`

- [ ] Code committed and pushed to both repositories

## Post-Deployment Tests

### 1. Basic Connectivity
- [ ] Backend URL accessible: https://payment-gateway-integration-371z.onrender.com
- [ ] Frontend URL accessible: https://payment-gateway-integration-ashen.vercel.app
- [ ] Both using HTTPS (not HTTP)

### 2. CSRF Token Test
Open browser DevTools → Network tab, then visit your frontend:

- [ ] Request to `/api/csrf/` returns 200 OK
- [ ] Response includes `csrftoken` cookie
- [ ] Cookie has `SameSite=None` and `Secure` flags

### 3. Authentication Flow
- [ ] Can access signup page
- [ ] Can create new account (POST `/api/auth/signup/`)
- [ ] Can login (POST `/api/auth/login/`)
- [ ] After login, `sessionid` cookie is set
- [ ] Can access user info (GET `/api/auth/user/`) - returns 200 OK
- [ ] Can logout (POST `/api/auth/logout/`)

### 4. Payment Flow
- [ ] Can create payment order
- [ ] Razorpay modal opens correctly
- [ ] Can complete test payment
- [ ] Payment verification works
- [ ] Transaction appears in history

### 5. Browser Console Checks
- [ ] No CORS errors
- [ ] No 403 Forbidden errors
- [ ] No "blocked by CORS policy" messages
- [ ] CSRF token logs show success

### 6. Cookie Inspection
Open DevTools → Application → Cookies:

- [ ] `csrftoken` cookie present
  - [ ] Domain: `.onrender.com` or your backend domain
  - [ ] SameSite: `None`
  - [ ] Secure: ✓
  - [ ] HttpOnly: (empty)

- [ ] `sessionid` cookie present (after login)
  - [ ] Domain: `.onrender.com` or your backend domain
  - [ ] SameSite: `None`
  - [ ] Secure: ✓
  - [ ] HttpOnly: ✓

## Troubleshooting

### If CSRF token not working:
1. Clear all cookies
2. Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
3. Try in incognito/private window
4. Check backend logs on Render

### If getting 403 Forbidden:
1. Verify `FRONTEND_URI` matches your Vercel URL exactly
2. Check `CORS_ALLOWED_ORIGINS` includes your Vercel URL
3. Ensure both sites use HTTPS
4. Clear cookies and try again

### If cookies not visible:
1. Check if backend is setting cookies (look at response headers)
2. Verify `withCredentials: true` in axios config
3. Ensure domains are correct in settings
4. Try the debug tool: `frontend/debug-cookies.html`

## Debug Commands

### Check backend logs on Render:
```bash
# In Render dashboard → Logs tab
# Look for CORS or authentication errors
```

### Test API directly with curl:
```bash
# Test CSRF endpoint
curl -i -X GET \
  https://payment-gateway-integration-371z.onrender.com/api/csrf/ \
  -H "Origin: https://payment-gateway-integration-ashen.vercel.app"

# Test user endpoint (should get 401 or 403)
curl -i -X GET \
  https://payment-gateway-integration-371z.onrender.com/api/auth/user/ \
  -H "Origin: https://payment-gateway-integration-ashen.vercel.app"
```

## Success Criteria

✅ All authentication flows work without errors
✅ No 403 Forbidden errors
✅ Cookies are set and visible in DevTools
✅ Payment flow completes successfully
✅ No CORS errors in console
✅ User can login, make payment, and logout smoothly
