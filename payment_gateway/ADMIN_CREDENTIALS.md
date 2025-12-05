# Django Admin Credentials

## Current Admin Access

### Local Development
- **URL**: http://localhost:8000/admin/
- **Username**: `abc`
- **Password**: `123`

### Production (Render)
- **URL**: https://payment-gateway-integration-371z.onrender.com/admin/
- **Username**: `abc`
- **Password**: `123`

## Quick Setup

### For Local
Already created! Just login with the credentials above.

### For Render (Production)

**Option 1: Environment Variables (Automatic)**

Add these to Render Dashboard → Environment:
```
DJANGO_SUPERUSER_USERNAME=abc
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=123
```

Then redeploy. The superuser will be created automatically.

**Option 2: Manual via Shell**

1. Go to Render Dashboard → Shell
2. Run:
```bash
python create_simple_admin.py
```

Or use Django's command:
```bash
python manage.py shell
```
```python
from django.contrib.auth.models import User
User.objects.create_superuser('abc', 'admin@example.com', '123')
exit()
```

## Security Warning ⚠️

**These are SIMPLE credentials for development/testing only!**

For production, you should:
1. Use a strong password (12+ characters, mixed case, numbers, symbols)
2. Use a real email address
3. Change credentials regularly
4. Enable 2FA if possible

## Change Password Later

To change to a stronger password:

```bash
# Local or Render Shell
python manage.py changepassword abc
```

Or update environment variables and redeploy.

## What You Can Do in Admin

✅ View and manage all users
✅ View all transactions and payments
✅ Update transaction statuses
✅ View payment logs for debugging
✅ Search and filter data
✅ Export data
✅ Manage user permissions

## Troubleshooting

### Can't login?
Run the create script again:
```bash
python create_simple_admin.py
```

### User exists but can't access admin?
Make user a superuser:
```bash
python manage.py shell
```
```python
from django.contrib.auth.models import User
user = User.objects.get(username='abc')
user.is_staff = True
user.is_superuser = True
user.save()
exit()
```

### Forgot to set on Render?
Use Render Shell and run:
```bash
python create_simple_admin.py
```

---

**Remember**: After deploying to production, consider changing these to more secure credentials!
