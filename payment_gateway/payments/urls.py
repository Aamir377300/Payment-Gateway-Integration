from django.urls import path
from . import views

urlpatterns = [
    path('create-order/', views.create_order_view, name='create_order'),
    path('verify-payment/', views.verify_payment_view, name='verify_payment'),
    path('success/<int:transaction_id>/', views.payment_success_view, name='payment_success'),
    path('failure/<int:transaction_id>/', views.payment_failure_view, name='payment_failure'),
    path('webhook/', views.webhook_handler, name='payment_webhook'),
    path('history/', views.transaction_history_view, name='transaction_history'),
]
