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
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"📝 Signup request received")
    logger.info(f"   Origin: {request.META.get('HTTP_ORIGIN', 'None')}")
    logger.info(f"   User-Agent: {request.META.get('HTTP_USER_AGENT', 'None')[:50]}")
    logger.info(f"   Cookies received: {list(request.COOKIES.keys())}")
    
    data = request.data

    first = data.get("first_name", "").strip()
    last = data.get("last_name", "").strip()
    email = data.get("email", "").strip()
    p1 = data.get("password1")
    p2 = data.get("password2")

    if not all([first, last, email, p1, p2]):
        logger.warning(f"   ❌ Missing required fields")
        return Response({"error": "All fields are required."}, status=400)

    if p1 != p2:
        logger.warning(f"   ❌ Passwords don't match")
        return Response({"error": "Passwords do not match."}, status=400)

    if User.objects.filter(email=email).exists():
        logger.warning(f"   ❌ Email already exists: {email}")
        return Response({"error": "Email already registered."}, status=400)

    user = User.objects.create_user(
        username=email,
        email=email,
        password=p1,
        first_name=first,
        last_name=last,
    )
    
    logger.info(f"   ✅ User created: {email}")

    return Response(
        {"message": "Account created.", "user": serialize_user(user)},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def login_api(request):
    import logging
    logger = logging.getLogger(__name__)
    
    email = request.data.get("email", "").strip()
    password = request.data.get("password")
    
    logger.info(f"🔑 Login attempt for: {email}")
    logger.info(f"   Origin: {request.META.get('HTTP_ORIGIN', 'None')}")
    logger.info(f"   Cookies received: {list(request.COOKIES.keys())}")

    if not email or not password:
        return Response({"error": "Email and password required."}, status=400)

    user = authenticate(request, username=email, password=password)

    if not user:
        logger.warning(f"   ❌ Authentication failed for: {email}")
        return Response({"error": "Invalid email or password."}, status=401)

    login(request, user)
    
    # Explicitly save the session
    request.session.save()
    
    logger.info(f"   ✅ Login successful for: {email}")
    logger.info(f"   Session Key: {request.session.session_key}")
    logger.info(f"   Session Data: {dict(request.session.items())}")
    
    response = Response({"message": "Login successful.", "user": serialize_user(user)})
    
    # Log response cookies
    logger.info(f"   Response cookies will be set")
    
    return response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_api(request):
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"🚪 Logout request from: {request.user.username}")
    logger.info(f"   Origin: {request.META.get('HTTP_ORIGIN', 'None')}")
    logger.info(f"   Session Key: {request.session.session_key}")
    
    logout(request)
    logger.info(f"   ✅ Logout successful")
    return Response({"message": "Logged out."})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def current_user_api(request):
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"👤 Current user check: {request.user.username}")
    logger.info(f"   Origin: {request.META.get('HTTP_ORIGIN', 'None')}")
    logger.info(f"   Session Key: {request.session.session_key}")
    logger.info(f"   Cookies: {list(request.COOKIES.keys())}")
    
    return Response(serialize_user(request.user))


@api_view(["GET"])
@permission_classes([AllowAny])
def csrf_token_api(request):
    """Endpoint to get CSRF token for cross-origin requests"""
    import logging
    from django.middleware.csrf import get_token
    
    logger = logging.getLogger(__name__)
    logger.info(f"🔐 CSRF token requested (legacy endpoint)")
    logger.info(f"   Origin: {request.META.get('HTTP_ORIGIN', 'None')}")
    logger.info(f"   Session exists: {bool(request.session.session_key)}")
    
    token = get_token(request)
    logger.info(f"   Token generated: {token[:10]}...")
    
    return Response({"csrfToken": token})
