import json
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.contrib.auth.models import User
from django.test import override_settings

from payments.models import Transaction
from payments.services import make_signature, sign_webhook

PASSWORD = 'Northwind#42'


def make_user(email='merchant@test.com'):
    return User.objects.create_user(username=email, email=email, password=PASSWORD, first_name='Mina')


def login(client, email='merchant@test.com'):
    client.post('/api/auth/login/', {
        'email': email,
        'password': PASSWORD,
    }, content_type='application/json')


@pytest.mark.django_db
class TestPayments:

    def test_create_order_in_sandbox(self, client):
        user = make_user()
        login(client)

        response = client.post('/api/payments/create-order/', {
            'amount': '500.00',
            'description': 'Test payment',
        }, content_type='application/json')

        assert response.status_code == 200
        body = response.data
        assert body['payment_mode'] == 'sandbox'
        assert body['razorpay_key_id'] == ''
        assert body['razorpay_order_id'].startswith('order_demo_')
        assert Transaction.objects.filter(user=user, status='PENDING', provider='sandbox').exists()

    def test_create_order_rejects_bad_amounts_and_blank_description(self, client):
        make_user()
        login(client)

        missing = client.post('/api/payments/create-order/', {
            'amount': '25',
            'description': '   ',
        }, content_type='application/json')
        assert missing.status_code == 400

        tiny = client.post('/api/payments/create-order/', {
            'amount': '0.50',
            'description': 'Too small',
        }, content_type='application/json')
        assert tiny.status_code == 400

        huge = client.post('/api/payments/create-order/', {
            'amount': '100000.01',
            'description': 'Too large',
        }, content_type='application/json')
        assert huge.status_code == 400

        messy = client.post('/api/payments/create-order/', {
            'amount': '10.999',
            'description': 'Too precise',
        }, content_type='application/json')
        assert messy.status_code == 400
        assert Transaction.objects.count() == 0

    def test_unauthenticated_cannot_create_order(self, client):
        response = client.post('/api/payments/create-order/', {
            'amount': '500.00',
            'description': 'Test',
        }, content_type='application/json')
        assert response.status_code == 403

    def test_sandbox_success_failure_and_idempotent_verify(self, client):
        make_user()
        login(client)
        created = client.post('/api/payments/create-order/', {
            'amount': '120.00',
            'description': 'Notebook',
        }, content_type='application/json')
        transaction_id = created.data['transaction']['id']
        order_id = created.data['razorpay_order_id']

        declined = client.post('/api/payments/create-order/', {
            'amount': '80.00',
            'description': 'Declined card',
        }, content_type='application/json')
        failed = client.post('/api/payments/sandbox/complete/', {
            'transaction_id': declined.data['transaction']['id'],
            'outcome': 'failed',
        }, content_type='application/json')
        assert failed.status_code == 200
        assert failed.data['transaction']['status'] == 'FAILED'
        assert 'declined' in failed.data['transaction']['failure_reason'].lower()

        success = client.post('/api/payments/sandbox/complete/', {
            'transaction_id': transaction_id,
            'outcome': 'success',
        }, content_type='application/json')
        assert success.status_code == 200
        payment_id = success.data['transaction']['razorpay_payment_id']
        assert payment_id.startswith('pay_demo_')

        again = client.post('/api/payments/verify/', {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': make_signature(order_id, payment_id),
        }, content_type='application/json')
        assert again.status_code == 200
        assert Transaction.objects.get(id=transaction_id).status == 'SUCCESS'

    def test_bad_signature_fails_the_payment(self, client):
        make_user()
        login(client)
        created = client.post('/api/payments/create-order/', {
            'amount': '50.00',
            'description': 'Forged',
        }, content_type='application/json')
        response = client.post('/api/payments/verify/', {
            'razorpay_order_id': created.data['razorpay_order_id'],
            'razorpay_payment_id': 'pay_fake',
            'razorpay_signature': 'not-a-real-signature',
        }, content_type='application/json')
        assert response.status_code == 400
        assert Transaction.objects.get(id=created.data['transaction']['id']).status == 'FAILED'

    def test_users_cannot_see_or_complete_someone_elses_payment(self, client):
        owner = make_user('owner@test.com')
        login(client, 'owner@test.com')
        created = client.post('/api/payments/create-order/', {
            'amount': '40.00',
            'description': 'Private',
        }, content_type='application/json')
        transaction_id = created.data['transaction']['id']
        client.post('/api/auth/logout/', content_type='application/json')

        make_user('other@test.com')
        login(client, 'other@test.com')

        detail = client.get(f'/api/payments/transactions/{transaction_id}/')
        assert detail.status_code == 404

        stolen = client.post('/api/payments/sandbox/complete/', {
            'transaction_id': transaction_id,
            'outcome': 'success',
        }, content_type='application/json')
        assert stolen.status_code == 404
        assert Transaction.objects.get(user=owner).status == 'PENDING'

    def test_failure_does_not_overwrite_success_and_cancel_marks_pending(self, client):
        make_user()
        login(client)
        created = client.post('/api/payments/create-order/', {
            'amount': '30.00',
            'description': 'Keep',
        }, content_type='application/json')
        transaction_id = created.data['transaction']['id']
        client.post('/api/payments/sandbox/complete/', {
            'transaction_id': transaction_id,
            'outcome': 'success',
        }, content_type='application/json')

        overwrite = client.post('/api/payments/failure/', {
            'transaction_id': transaction_id,
        }, content_type='application/json')
        assert overwrite.status_code == 200
        assert overwrite.data['transaction']['status'] == 'SUCCESS'

        pending = client.post('/api/payments/create-order/', {
            'amount': '15.00',
            'description': 'Abandoned',
        }, content_type='application/json')
        cancelled = client.post('/api/payments/failure/', {
            'transaction_id': pending.data['transaction']['id'],
            'reason': 'Checkout was cancelled.',
        }, content_type='application/json')
        assert cancelled.data['transaction']['status'] == 'FAILED'
        assert cancelled.data['transaction']['failure_reason'] == 'Checkout was cancelled.'

    def test_refund_only_successful_sandbox_payments(self, client):
        make_user()
        login(client)
        created = client.post('/api/payments/create-order/', {
            'amount': '60.00',
            'description': 'Refund me',
        }, content_type='application/json')
        transaction_id = created.data['transaction']['id']

        too_soon = client.post(f'/api/payments/transactions/{transaction_id}/refund/')
        assert too_soon.status_code == 400

        client.post('/api/payments/sandbox/complete/', {
            'transaction_id': transaction_id,
            'outcome': 'success',
        }, content_type='application/json')
        refunded = client.post(f'/api/payments/transactions/{transaction_id}/refund/')
        assert refunded.status_code == 200
        assert refunded.data['transaction']['status'] == 'REFUNDED'

        again = client.post(f'/api/payments/transactions/{transaction_id}/refund/')
        assert again.status_code == 400

    def test_history_filters_summary_and_export(self, client):
        user = make_user()
        login(client)
        Transaction.objects.create(
            user=user, order_id='ORD-1', amount=Decimal('500.00'), status='SUCCESS',
            description='Studio invoice', razorpay_payment_id='pay_studio', provider='sandbox',
        )
        Transaction.objects.create(
            user=user, order_id='ORD-2', amount=Decimal('20.00'), status='FAILED',
            description='Poster print', provider='sandbox',
        )
        Transaction.objects.create(
            user=user, order_id='ORD-3', amount=Decimal('15.00'), status='REFUNDED',
            description='Domain', provider='sandbox',
        )

        history = client.get('/api/payments/transactions/?status=SUCCESS&q=studio')
        assert history.status_code == 200
        assert history.data['count'] == 1
        assert history.data['results'][0]['order_id'] == 'ORD-1'

        summary = client.get('/api/payments/summary/')
        assert summary.data['successful_count'] == 1
        assert summary.data['collected_amount'] == '500.00'
        assert summary.data['refunded_amount'] == '15.00'
        assert summary.data['failed_count'] == 1

        exported = client.get('/api/payments/transactions/export/?status=FAILED')
        assert exported.status_code == 200
        body = exported.content.decode()
        assert 'Poster print' in body
        assert 'Studio invoice' not in body

    def test_sandbox_cannot_complete_a_provider_order(self, client):
        user = make_user()
        login(client)
        transaction = Transaction.objects.create(
            user=user,
            order_id='ORD-LIVE',
            amount=Decimal('10.00'),
            status='PENDING',
            provider='razorpay',
            description='Live',
            razorpay_order_id='order_live_1',
        )
        response = client.post('/api/payments/sandbox/complete/', {
            'transaction_id': transaction.id,
            'outcome': 'success',
        }, content_type='application/json')
        assert response.status_code == 400
        transaction.refresh_from_db()
        assert transaction.status == 'PENDING'

    def test_webhook_requires_a_valid_signature(self, client):
        user = make_user()
        transaction = Transaction.objects.create(
            user=user,
            order_id='ORD-HOOK',
            amount=Decimal('75.00'),
            status='PENDING',
            provider='sandbox',
            description='Webhook',
            razorpay_order_id='order_demo_hook',
        )
        payload = {
            'event': 'payment.captured',
            'payload': {'payment': {'entity': {'order_id': 'order_demo_hook', 'id': 'pay_hook_1'}}},
        }
        raw = json.dumps(payload).encode()

        rejected = client.post(
            '/api/payments/webhook/',
            data=raw,
            content_type='application/json',
            HTTP_X_RAZORPAY_SIGNATURE='bad',
        )
        assert rejected.status_code == 400
        transaction.refresh_from_db()
        assert transaction.status == 'PENDING'

        accepted = client.post(
            '/api/payments/webhook/',
            data=raw,
            content_type='application/json',
            HTTP_X_RAZORPAY_SIGNATURE=sign_webhook(raw),
        )
        assert accepted.status_code == 200
        assert accepted.json()['status'] == 'processed'
        transaction.refresh_from_db()
        assert transaction.status == 'SUCCESS'
        assert transaction.razorpay_payment_id == 'pay_hook_1'

        failed_payment = Transaction.objects.create(
            user=user,
            order_id='ORD-HOOK-2',
            amount=Decimal('10.00'),
            status='PENDING',
            provider='sandbox',
            description='Webhook fail',
            razorpay_order_id='order_demo_hook_2',
        )
        fail_payload = {
            'event': 'payment.failed',
            'payload': {'payment': {'entity': {'order_id': 'order_demo_hook_2', 'id': 'pay_hook_2'}}},
        }
        fail_raw = json.dumps(fail_payload).encode()
        failed = client.post(
            '/api/payments/webhook/',
            data=fail_raw,
            content_type='application/json',
            HTTP_X_RAZORPAY_SIGNATURE=sign_webhook(fail_raw),
        )
        assert failed.json()['status'] == 'processed'
        failed_payment.refresh_from_db()
        assert failed_payment.status == 'FAILED'

    @override_settings(PAYMENT_MODE='razorpay', RAZORPAY_KEY_ID='rzp_test_portfolio', RAZORPAY_KEY_SECRET='secret')
    @patch('razorpay.Client')
    def test_razorpay_mode_creates_a_provider_order(self, mock_client, client):
        make_user()
        login(client)
        mock_client.return_value.order.create.return_value = {
            'id': 'order_live_99',
            'amount': 25000,
            'currency': 'INR',
            'receipt': 'receipt',
        }

        response = client.post('/api/payments/create-order/', {
            'amount': '250.00',
            'description': 'Live order',
        }, content_type='application/json')

        assert response.status_code == 200
        assert response.data['payment_mode'] == 'razorpay'
        assert response.data['charge_mode'] == 'test'
        assert response.data['razorpay_order_id'] == 'order_live_99'
        assert response.data['razorpay_key_id'] == 'rzp_test_portfolio'
        assert Transaction.objects.get().provider == 'razorpay'

    @override_settings(PAYMENT_MODE='razorpay', RAZORPAY_KEY_ID='rzp_test_portfolio', RAZORPAY_KEY_SECRET='secret')
    @patch('razorpay.Client')
    def test_razorpay_outage_marks_the_order_failed(self, mock_client, client):
        make_user()
        login(client)
        mock_client.return_value.order.create.side_effect = Exception('provider down')

        response = client.post('/api/payments/create-order/', {
            'amount': '250.00',
            'description': 'Live order',
        }, content_type='application/json')

        assert response.status_code == 502
        assert Transaction.objects.get().status == 'FAILED'

    @override_settings(PAYMENT_MODE='auto', RAZORPAY_KEY_ID='rzp_test_portfolio', RAZORPAY_KEY_SECRET='secret')
    def test_test_keys_turn_on_razorpay_without_code_changes(self, client):
        config = client.get('/api/config/')
        assert config.status_code == 200
        assert config.data['payment_mode'] == 'razorpay'
        assert config.data['charge_mode'] == 'test'
        assert 'demo_login' not in config.data

    @override_settings(PAYMENT_MODE='auto', RAZORPAY_KEY_ID='rzp_live_portfolio', RAZORPAY_KEY_SECRET='secret')
    def test_live_keys_are_a_real_charge(self, client):
        config = client.get('/api/config/')
        assert config.data['payment_mode'] == 'razorpay'
        assert config.data['charge_mode'] == 'live'
