from django.contrib import admin
from django.http import JsonResponse
from django.urls import path
from django.views.decorators.csrf import ensure_csrf_cookie

from accounts.views import current_user_api, login_api, logout_api, signup_api
from payments.services import DEMO_EMAIL, DEMO_PASSWORD, PaymentError, charge_mode, payment_mode
from payments.views import (
    create_order_api,
    export_transactions_api,
    health_api,
    payment_failure_api,
    refund_api,
    sandbox_complete_api,
    transaction_detail_api,
    transaction_history_api,
    transaction_summary_api,
    verify_payment_api,
    webhook_api,
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'detail': 'CSRF cookie set'})


@api_view(['GET'])
@permission_classes([AllowAny])
def public_config_api(request):
    try:
        mode = payment_mode()
        charges = charge_mode()
    except PaymentError:
        mode = 'misconfigured'
        charges = 'misconfigured'
    data = {
        'payment_mode': mode,
        'charge_mode': charges,
        'demo_email': DEMO_EMAIL,
    }
    if mode == 'sandbox':
        data['demo_login'] = {
            'email': DEMO_EMAIL,
            'password': DEMO_PASSWORD,
        }
    return Response(data)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health_api, name='api_health'),
    path('api/config/', public_config_api, name='api_config'),
    path('api/csrf/', get_csrf_token, name='api_csrf'),

    path('api/auth/signup/', signup_api, name='api_signup'),
    path('api/auth/login/', login_api, name='api_login'),
    path('api/auth/logout/', logout_api, name='api_logout'),
    path('api/auth/user/', current_user_api, name='api_current_user'),

    path('api/payments/create-order/', create_order_api, name='api_create_order'),
    path('api/payments/verify/', verify_payment_api, name='api_verify_payment'),
    path('api/payments/failure/', payment_failure_api, name='api_payment_failure'),
    path('api/payments/sandbox/complete/', sandbox_complete_api, name='api_sandbox_complete'),
    path('api/payments/summary/', transaction_summary_api, name='api_transaction_summary'),
    path('api/payments/transactions/', transaction_history_api, name='api_transaction_history'),
    path('api/payments/transactions/export/', export_transactions_api, name='api_export_transactions'),
    path('api/payments/transactions/<int:transaction_id>/', transaction_detail_api, name='api_transaction_detail'),
    path('api/payments/transactions/<int:transaction_id>/refund/', refund_api, name='api_refund'),
    path('api/payments/webhook/', webhook_api, name='api_webhook'),
]
