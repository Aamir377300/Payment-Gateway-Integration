#!/usr/bin/env python
"""
Create simple admin user: username=abc, password=123
Run with: python create_simple_admin.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'payment_gateway.settings')
django.setup()

from django.contrib.auth.models import User

def create_simple_admin():
    username = "abc"
    email = "admin@example.com"
    password = "123"
    
    # Check if user already exists
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        # Update to make sure they're a superuser
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()
        print(f"✅ Updated existing user '{username}' to superuser")
    else:
        # Create new superuser
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f"✅ Created new superuser '{username}'")
    
    print(f"\n📝 Admin Credentials:")
    print(f"   Username: {username}")
    print(f"   Password: {password}")
    print(f"\n🔗 Access admin at:")
    print(f"   Local: http://localhost:8000/admin/")
    print(f"   Render: https://payment-gateway-integration-371z.onrender.com/admin/")

if __name__ == "__main__":
    try:
        create_simple_admin()
    except Exception as e:
        print(f"❌ Error: {e}")
