from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from accounts.views import signup_api, login_api, logout_api, current_user_api
from payments.views import (
    create_order_api, verify_payment_api, payment_failure_api,
    transaction_history_api, transaction_detail_api
)


@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'detail': 'CSRF cookie set'})


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # CSRF token
    path('api/csrf/', get_csrf_token, name='api_csrf'),
    
    # Auth API endpoints
    path('api/auth/signup/', signup_api, name='api_signup'),
    path('api/auth/login/', login_api, name='api_login'),
    path('api/auth/logout/', logout_api, name='api_logout'),
    path('api/auth/user/', current_user_api, name='api_current_user'),
    
    # Payment API endpoints
    path('api/payments/create-order/', create_order_api, name='api_create_order'),
    path('api/payments/verify/', verify_payment_api, name='api_verify_payment'),
    path('api/payments/failure/', payment_failure_api, name='api_payment_failure'),
    path('api/payments/transactions/', transaction_history_api, name='api_transaction_history'),
    path('api/payments/transactions/<int:transaction_id>/', transaction_detail_api, name='api_transaction_detail'),
]
