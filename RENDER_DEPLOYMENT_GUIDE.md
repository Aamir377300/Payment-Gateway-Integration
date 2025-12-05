# Render Deployment Troubleshooting Guide

## Current Issue: 500 Internal Server Error on Login

The 500 error means your backend is crashing. Most common causes:

### 1. Database Not Migrated ⚠️ MOST LIKELY

**Problem:** Django tables don't exist in your PostgreSQL database.

**Solution:**

1. Go to Render Dashboard → Your Web Service
2. Click "Shell" tab (or use SSH)
3. Run these commands:

```bash
python manage.py migrate
python manage.py createsuperuser  # Optional but recommended
```

**Or add to your build command:**

In Render dashboard → Settings → Build Command:
```bash
pip install -r requirements.txt && python manage.py migrate
```

### 2. Environment Variables Not Set

**Required Environment Variables on Render:**

```
DEBUG=False
SECRET_KEY=<your-secret-key>
FRONTEND_URI=https://payment-gateway-integration-ashen.vercel.app
RAZORPAY_KEY_ID=rzp_test_RnRBP2wR9RNuMV
RAZORPAY_KEY_SECRET=KSKppx0QVEPZ4hEIVdrqp891
DATABASE_URL=<auto-set-by-render>
```

**How to check:**
1. Render Dashboard → Your Service → Environment
2. Verify all variables are set
3. Click "Save Changes" if you add any

### 3. Database Connection Issue

**Check if PostgreSQL is connected:**

1. Render Dashboard → Your Web Service → Environment
2. Look for `DATABASE_URL` - should be auto-populated
3. If missing, go to your PostgreSQL database and copy the Internal Database URL
4. Add it manually as `DATABASE_URL`

### 4. Check Render Logs

**How to view logs:**

1. Render Dashboard → Your Web Service
2. Click "Logs" tab
3. Look for error messages like:
   - `relation "auth_user" does not exist` → Need to run migrations
   - `could not connect to server` → Database connection issue
   - `SECRET_KEY` → Environment variable missing

## Step-by-Step Fix

### Step 1: Check Health Endpoint

I've added a health check endpoint. Test it:

```bash
curl https://payment-gateway-integration-371z.onrender.com/api/health/
```

This will tell you:
- ✅ Database connection status
- ✅ Number of users in database
- ✅ Environment variables status

### Step 2: Run Migrations on Render

**Option A: Via Shell**
1. Render Dashboard → Your Service → Shell
2. Run:
```bash
python manage.py migrate
python manage.py createsuperuser
```

**Option B: Update Build Command**
1. Render Dashboard → Settings → Build Command
2. Change to:
```bash
pip install -r requirements.txt && python manage.py migrate
```
3. Save and trigger manual deploy

### Step 3: Verify Environment Variables

Check these are set in Render:
- [ ] `DEBUG=False`
- [ ] `SECRET_KEY` (not empty)
- [ ] `FRONTEND_URI` (your Vercel URL)
- [ ] `DATABASE_URL` (auto-set, should exist)
- [ ] `RAZORPAY_KEY_ID`
- [ ] `RAZORPAY_KEY_SECRET`

### Step 4: Check Logs for Specific Error

1. Go to Render Logs
2. Look for the actual Python error
3. Common errors:

**"relation auth_user does not exist"**
```
Solution: Run migrations (Step 2)
```

**"CSRF verification failed"**
```
Solution: Already fixed in settings.py
```

**"could not connect to database"**
```
Solution: Check DATABASE_URL is set correctly
```

## Render Configuration Files

### Build Command
```bash
pip install -r requirements.txt && python manage.py migrate
```

### Start Command
```bash
gunicorn payment_gateway.wsgi:application
```

### Environment Variables
```
DEBUG=False
SECRET_KEY=django-insecure-3bytsxp$ozrsp0@=
FRONTEND_URI=https://payment-gateway-integration-ashen.vercel.app
RAZORPAY_KEY_ID=rzp_test_RnRBP2wR9RNuMV
RAZORPAY_KEY_SECRET=KSKppx0QVEPZ4hEIVdrqp891
PYTHON_VERSION=3.11.0
```

## Testing After Fix

### 1. Test Health Endpoint
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

### 2. Test CSRF Endpoint
```bash
curl https://payment-gateway-integration-371z.onrender.com/api/csrf/
```

Expected: 200 OK with JSON response

### 3. Test Signup
```bash
curl -X POST https://payment-gateway-integration-371z.onrender.com/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Test",
    "last_name": "User",
    "email": "test@example.com",
    "password1": "testpass123",
    "password2": "testpass123"
  }'
```

Expected: 201 Created with user data

### 4. Test Login
```bash
curl -X POST https://payment-gateway-integration-371z.onrender.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

Expected: 200 OK with user data

## Common Render Issues

### Issue: "Your service is taking longer than expected to start"
**Solution:** 
- Free tier can be slow on first start
- Wait 2-3 minutes
- Check logs for actual errors

### Issue: Service keeps restarting
**Solution:**
- Check logs for Python errors
- Verify `gunicorn` is in requirements.txt
- Check start command is correct

### Issue: Database connection timeout
**Solution:**
- Ensure PostgreSQL service is running
- Check DATABASE_URL is set
- Verify database and web service are in same region

### Issue: Static files not loading
**Solution:**
- Not needed for API-only backend
- If needed, add whitenoise to requirements.txt

## Quick Diagnostic Checklist

Run these in order:

1. **Check service is running:**
   ```bash
   curl https://payment-gateway-integration-371z.onrender.com/api/health/
   ```

2. **Check Render logs:**
   - Look for migration errors
   - Look for database connection errors
   - Look for missing environment variables

3. **Verify database:**
   - PostgreSQL service is running
   - DATABASE_URL is set
   - Migrations have been run

4. **Test locally first:**
   ```bash
   cd payment_gateway
   python manage.py runserver
   # Try login at http://localhost:8000/api/auth/login/
   ```

## Need More Help?

1. **Share Render logs** - Copy the error from Render logs
2. **Test health endpoint** - Share the response from `/api/health/`
3. **Check database** - Verify PostgreSQL is running on Render
