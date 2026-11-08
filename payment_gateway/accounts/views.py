from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


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

    first = (data.get("first_name") or "").strip()
    last = (data.get("last_name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password1") or ""
    confirmation = data.get("password2") or ""

    if not all([first, last, email, password, confirmation]):
        return Response({"error": "All fields are required."}, status=400)

    if len(first) > 150 or len(last) > 150:
        return Response({"error": "Name is too long."}, status=400)

    try:
        validate_email(email)
    except ValidationError:
        return Response({"error": "Enter a valid email address."}, status=400)

    if password != confirmation:
        return Response({"error": "Passwords do not match."}, status=400)

    if User.objects.filter(email__iexact=email).exists() or User.objects.filter(username__iexact=email).exists():
        return Response({"error": "Email already registered."}, status=400)

    candidate = User(username=email, email=email, first_name=first, last_name=last)
    try:
        validate_password(password, candidate)
    except ValidationError as exc:
        return Response({"error": exc.messages[0]}, status=400)

    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
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
    email = (request.data.get("email") or "").strip().lower()
    password = request.data.get("password") or ""

    if not email or not password:
        return Response({"error": "Email and password required."}, status=400)

    user = authenticate(request, username=email, password=password)

    if not user:
        return Response({"error": "Invalid email or password."}, status=401)

    login(request, user)
    request.session.save()

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
