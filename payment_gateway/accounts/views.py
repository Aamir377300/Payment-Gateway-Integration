from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

# it converts a Django User model object into a JSON-friendly Python dictionary that can be sent to the frontend (React). 
def serialize_user(user):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }


@api_view(["POST"])
@permission_classes([AllowAny])
def signup_api(request):
    data = request.data

    first = data.get("first_name", "").strip()
    last = data.get("last_name", "").strip()
    email = data.get("email", "").strip()
    p1 = data.get("password1")
    p2 = data.get("password2")

    if not all([first, last, email, p1, p2]):
        return Response({"error": "All fields are required."}, status=400)

    if p1 != p2:
        return Response({"error": "Passwords do not match."}, status=400)

    if User.objects.filter(email=email).exists():
        return Response({"error": "Email already registered."}, status=400)

    user = User.objects.create_user(
        username=email,
        email=email,
        password=p1,
        first_name=first,
        last_name=last,
    )

    return Response(
        {"message": "Account created.", "user": serialize_user(user)},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def login_api(request):
    email = request.data.get("email", "").strip()
    password = request.data.get("password")

    if not email or not password:
        return Response({"error": "Email and password required."}, status=400)

    user = authenticate(request, username=email, password=password)

    if not user:
        return Response({"error": "Invalid email or password."}, status=401)

    login(request, user)
    return Response({"message": "Login successful.", "user": serialize_user(user)})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_api(request):
    logout(request)
    return Response({"message": "Logged out."})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def current_user_api(request):
    return Response(serialize_user(request.user))


@api_view(["GET"])
@permission_classes([AllowAny])
def csrf_token_api(request):
    """Endpoint to get CSRF token for cross-origin requests"""
    from django.middleware.csrf import get_token
    csrf_token = get_token(request)
    
    # Debug info (remove in production if needed)
    response_data = {
        "csrfToken": csrf_token,
        "message": "CSRF token generated successfully"
    }
    
    return Response(response_data)


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check_api(request):
    """Health check endpoint to verify backend is working"""
    import os
    from django.db import connection
    
    health_status = {
        "status": "ok",
        "database": "unknown",
        "debug": os.getenv('DEBUG', 'not set'),
        "frontend_url": os.getenv('FRONTEND_URI', 'not set'),
    }
    
    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status["database"] = "connected"
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
        health_status["status"] = "error"
    
    # Check if User table exists
    try:
        user_count = User.objects.count()
        health_status["users_count"] = user_count
    except Exception as e:
        health_status["users_table"] = f"error: {str(e)}"
        health_status["status"] = "error"
    
    return Response(health_status)
