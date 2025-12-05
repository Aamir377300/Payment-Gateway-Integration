#!/usr/bin/env python
"""
Quick script to create a superuser for Django admin
Run with: python create_superuser.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'payment_gateway.settings')
django.setup()

from django.contrib.auth.models import User

def create_superuser():
    username = input("Enter username (default: admin): ").strip() or "admin"
    email = input("Enter email: ").strip()
    
    if User.objects.filter(username=username).exists():
        print(f"❌ User '{username}' already exists!")
        return
    
    if email and User.objects.filter(email=email).exists():
        print(f"❌ Email '{email}' is already registered!")
        return
    
    password = input("Enter password: ").strip()
    
    if len(password) < 8:
        print("❌ Password must be at least 8 characters!")
        return
    
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    
    print(f"\n✅ Superuser '{username}' created successfully!")
    print(f"📧 Email: {email}")
    print(f"\n🔗 Access admin at: http://localhost:8000/admin/")

if __name__ == "__main__":
    try:
        create_superuser()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
