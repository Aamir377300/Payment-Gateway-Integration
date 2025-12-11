"""
Simple Payment Tests
Run: pytest tests/test_payments.py -v
"""
import pytest
from django.contrib.auth.models import User
from payments.models import Transaction
from decimal import Decimal
from unittest.mock import patch, MagicMock


@pytest.mark.django_db
class TestPayments:
    
    @patch('payments.views.get_razorpay_client')
    def test_create_order(self, mock_razorpay, client):
        user = User.objects.create_user(
            username='test@test.com',
            email='test@test.com',
            password='testpass123'
        )
        client.force_login(user)
        
        mock_client = MagicMock()
        mock_client.order.create.return_value = {
            'id': 'order_123',
            'amount': 50000,
            'currency': 'INR',
            'receipt': 'ORD_1_1'
        }
        mock_razorpay.return_value = mock_client
        
        response = client.post('/api/payments/create-order/', {
            'amount': '500.00',
            'description': 'Test payment'
        }, content_type='application/json')
        
        assert response.status_code == 200
        assert Transaction.objects.filter(user=user).exists()
    
    def test_get_transactions(self, client):
        user = User.objects.create_user(
            username='test@test.com',
            email='test@test.com',
            password='testpass123'
        )
        client.force_login(user)
        
        Transaction.objects.create(
            user=user,
            order_id='ORD_1',
            amount=Decimal('500.00'),
            currency='INR',
            status='SUCCESS'
        )
        
        response = client.get('/api/payments/transactions/')
        
        assert response.status_code == 200
        assert len(response.data) == 1
    
    def test_unauthenticated_cannot_create_order(self, client):
        response = client.post('/api/payments/create-order/', {
            'amount': '500.00',
            'description': 'Test'
        }, content_type='application/json')
        
        assert response.status_code == 403
