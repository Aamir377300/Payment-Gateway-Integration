# 🚀 Action Plan to Fix 500 Error

## Current Situation

- ✅ CORS and cookie configuration fixed locally
- ✅ Frontend pointing to correct backend URL
- ❌ Backend on Render returning 500 error on login
- ❌ Changes not deployed to Render yet

## Root Cause

The 500 error is most likely because **database migrations haven't been run** on Render. The `auth_user` table doesn't exist in your PostgreSQL database.

## Step-by-Step Fix

### Step 1: Deploy Updated Code to Render

```bash
cd payment_gateway
git add .
git commit -m "Add health check endpoint and fix CORS configuration"
git push
```

This will trigger automatic deployment on Render.

### Step 2: Run Database Migrations on Render

**Option A: Via Render Shell (Recommended)**

1. Go to https://dashboard.render.com
2. Click on your web service
3. Click "Shell" tab
4. Run these commands:

```bash
python manage.py migrate
python manage.py createsuperuser  # Create admin user (optional)
```

**Option B: Update Build Command**

1. Go to Render Dashboard → Your Service → Settings
2. Find "Build Command"
3. Change from:
   ```
   pip install -r requirements.txt
   ```
   To:
   ```
   pip install -r requirements.txt && python manage.py migrate
   ```
4. Click "Save Changes"
5. Trigger manual deploy

### Step 3: Verify Environment Variables on Render

Go to Render Dashboard → Environment and ensure these are set:

```
DEBUG=False
SECRET_KEY=django-insecure-3bytsxp$ozrsp0@=
FRONTEND_URI=https://payment-gateway-integration-ashen.vercel.app
RAZORPAY_KEY_ID=rzp_test_RnRBP2wR9RNuMV
RAZORPAY_KEY_SECRET=KSKppx0QVEPZ4hEIVdrqp891
DATABASE_URL=(should be auto-set)
```

### Step 4: Test Backend Health

After deployment completes, run:

```bash
./test-backend-health.sh
```

Or manually test:
```bash
curl https://payment-gateway-integration-371z.onrender.com/api/health/
```

Expected response:
```json
{
  "status": "ok",
  "database": "connected",
  "users_count": 0,
  "debug": "False",
  "frontend_url": "https://payment-gateway-integration-ashen.vercel.app"
}
```

### Step 5: Deploy Frontend to Vercel

```bash
cd frontend
git add .
git commit -m "Fix authentication error handling"
git push
```

### Step 6: Update Vercel Environment Variable

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add or update:
   ```
   VITE_API_URL=https://payment-gateway-integration-371z.onrender.com/api
   ```
3. Redeploy from Vercel dashboard

### Step 7: Test Complete Flow

1. Clear browser cookies
2. Visit your Vercel app
3. Try to signup with a new account
4. Try to login
5. Check that no 403 or 500 errors appear

## What Each Step Does

| Step | Purpose | Expected Result |
|------|---------|-----------------|
| 1 | Deploy code changes | New code on Render |
| 2 | Create database tables | `auth_user` table exists |
| 3 | Configure environment | Backend knows frontend URL |
| 4 | Verify backend works | Health check returns OK |
| 5 | Deploy frontend | Updated error handling |
| 6 | Configure frontend | Points to correct backend |
| 7 | End-to-end test | Everything works |

## Troubleshooting

### If Step 2 fails (migrations)

Check Render logs:
```
Render Dashboard → Your Service → Logs
```

Look for:
- Database connection errors
- Missing DATABASE_URL
- Permission errors

### If Step 4 fails (health check)

1. Check if service is running on Render
2. Check Render logs for Python errors
3. Verify DATABASE_URL is set
4. Try restarting the service

### If Step 7 fails (login still 500)

1. Check Render logs during login attempt
2. Look for specific Python error
3. Verify migrations completed successfully
4. Check if user table exists:
   ```bash
   # In Render shell
   python manage.py dbshell
   \dt  # List tables
   \q   # Quit
   ```

## Quick Commands Reference

**Test backend health:**
```bash
./test-backend-health.sh
```

**Test API endpoints:**
```bash
./test-api.sh
```

**Check Render logs:**
```
https://dashboard.render.com → Your Service → Logs
```

**Run migrations on Render:**
```bash
# In Render Shell
python manage.py migrate
```

**Create superuser on Render:**
```bash
# In Render Shell
python manage.py createsuperuser
```

## Expected Timeline

- Step 1-2: 5-10 minutes (Render deployment + migrations)
- Step 3: 2 minutes (verify env vars)
- Step 4: 1 minute (test health)
- Step 5-6: 3-5 minutes (Vercel deployment)
- Step 7: 2 minutes (testing)

**Total: ~15-20 minutes**

## Success Criteria

✅ Health endpoint returns `"status": "ok"`
✅ Health endpoint shows `"database": "connected"`
✅ Can signup new user (201 Created)
✅ Can login (200 OK)
✅ Can access user info after login (200 OK)
✅ No 403 or 500 errors in browser console
✅ Cookies visible in DevTools with correct flags

## Still Having Issues?

If you complete all steps and still have errors:

1. **Share Render logs** - Copy the error from logs
2. **Share health check response** - Run `./test-backend-health.sh`
3. **Share browser console errors** - Screenshot or copy errors
4. **Check database** - Verify PostgreSQL service is running on Render
