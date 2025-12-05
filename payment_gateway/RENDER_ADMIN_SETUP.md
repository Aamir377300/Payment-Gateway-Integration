# Setting Up Admin Access on Render

## Method 1: Using Render Shell (Easiest)

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com
   - Select your `payment-gateway` service

2. **Open Shell**
   - Click on **"Shell"** tab in the left sidebar
   - Wait for the shell to connect

3. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```
   
4. **Enter Details**
   - Username: `admin` (or your choice)
   - Email: your email
   - Password: strong password (min 8 chars)
   - Confirm password

5. **Access Admin**
   - Go to: `https://payment-gateway-integration-371z.onrender.com/admin/`
   - Login with your credentials

---

## Method 2: Automated via Environment Variables

1. **Add Environment Variables in Render**
   - Go to your service → **Environment** tab
   - Add these variables:
   
   ```
   DJANGO_SUPERUSER_USERNAME=admin
   DJANGO_SUPERUSER_EMAIL=your@email.com
   DJANGO_SUPERUSER_PASSWORD=YourStrongPassword123!
   ```

2. **Redeploy**
   - The `build.sh` script will automatically create the superuser
   - Check logs to confirm: "✅ Superuser 'admin' created successfully!"

3. **Access Admin**
   - Go to: `https://payment-gateway-integration-371z.onrender.com/admin/`
   - Login with the credentials you set

---

## Method 3: Using Django Shell

If Method 1 doesn't work:

1. **Open Render Shell**
   ```bash
   python manage.py shell
   ```

2. **Run Python Commands**
   ```python
   from django.contrib.auth.models import User
   User.objects.create_superuser('admin', 'admin@example.com', 'your_password')
   exit()
   ```

3. **Access Admin**
   - Go to admin URL and login

---

## Troubleshooting

### "User already exists"
- The superuser is already created
- Try logging in with existing credentials
- Or create a new user with different username

### "Shell not available"
- Wait a few seconds and try again
- Make sure your service is running (not sleeping)
- Check if you're on a paid plan (free tier has limitations)

### "Permission denied"
- Make sure `build.sh` is executable:
  ```bash
  chmod +x build.sh
  ```

### Can't access admin page
- Check if service is running
- Verify URL: `https://your-service.onrender.com/admin/`
- Check browser console for errors
- Verify `django.contrib.admin` is in INSTALLED_APPS

---

## Security Tips

1. **Use Strong Passwords**
   - Minimum 12 characters
   - Mix of letters, numbers, symbols

2. **Don't Commit Credentials**
   - Never commit superuser passwords to git
   - Use environment variables only

3. **Limit Admin Access**
   - Only create admin accounts for trusted users
   - Use staff accounts for limited access

4. **Monitor Admin Activity**
   - Check Django admin logs regularly
   - Review user permissions periodically

---

## Quick Access

- **Admin URL**: https://payment-gateway-integration-371z.onrender.com/admin/
- **Render Dashboard**: https://dashboard.render.com
- **Shell Command**: `python manage.py createsuperuser`
