# Environment Variables Checklist

## Render (Backend) - Required Environment Variables

Set these in your Render dashboard under "Environment":

```
DEBUG=False
SECRET_KEY=django-insecure-3bytsxp$ozrsp0@=
FRONTEND_URI=https://payment-gateway-integration-ashen.vercel.app
RAZORPAY_KEY_ID=rzp_test_RnRBP2wR9RNuMV
RAZORPAY_KEY_SECRET=KSKppx0QVEPZ4hEIVdrqp891
DATABASE_URL=(auto-set by Render)
```

## Vercel (Frontend) - Required Environment Variables

Set these in your Vercel project settings under "Environment Variables":

```
VITE_API_URL=https://payment-gateway-integration-371z.onrender.com/api
```

## Important Notes

1. **Render DATABASE_URL** is automatically set when you add a PostgreSQL database
2. **SECRET_KEY** should be a long random string in production (generate a new one!)
3. **DEBUG** must be `False` in production for security
4. **FRONTEND_URI** must match your actual Vercel deployment URL
5. After changing environment variables, you must redeploy both services

## Generate a New SECRET_KEY (Recommended)

Run this in Python:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

Or use this one-liner:
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```
