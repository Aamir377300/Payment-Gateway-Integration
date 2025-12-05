#!/usr/bin/env python
"""
Auto-create superuser from environment variables
Safe to run multiple times - only creates if user doesn't exist
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'payment_gateway.settings')
django.setup()

from django.contrib.auth.models import User

def create_admin_from_env():
    username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
    email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
    password = os.getenv('DJANGO_SUPERUSER_PASSWORD')
    
    if not password:
        print("⚠️  DJANGO_SUPERUSER_PASSWORD not set. Skipping superuser creation.")
        return
    
    if User.objects.filter(username=username).exists():
        print(f"✅ Superuser '{username}' already exists.")
        return
    
    try:
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f"✅ Superuser '{username}' created successfully!")
        print(f"📧 Email: {email}")
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")

if __name__ == "__main__":
    create_admin_from_env()
