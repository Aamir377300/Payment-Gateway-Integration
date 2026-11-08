import pytest
from django.contrib.auth.models import User

PASSWORD = 'Northwind#42'


@pytest.mark.django_db
class TestAuthentication:

    def test_user_signup(self, client):
        response = client.post('/api/auth/signup/', {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'John@test.com',
            'password1': PASSWORD,
            'password2': PASSWORD,
        }, content_type='application/json')

        assert response.status_code == 201
        user = User.objects.get(email='john@test.com')
        assert user.username == 'john@test.com'
        assert user.check_password(PASSWORD)

    def test_signup_rejects_mismatched_passwords(self, client):
        response = client.post('/api/auth/signup/', {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@test.com',
            'password1': PASSWORD,
            'password2': 'Other#42pass',
        }, content_type='application/json')

        assert response.status_code == 400
        assert not User.objects.filter(email='john@test.com').exists()

    def test_signup_rejects_short_password(self, client):
        response = client.post('/api/auth/signup/', {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@test.com',
            'password1': 'short',
            'password2': 'short',
        }, content_type='application/json')

        assert response.status_code == 400

    def test_signup_rejects_duplicate_email(self, client):
        User.objects.create_user(username='john@test.com', email='john@test.com', password=PASSWORD)
        response = client.post('/api/auth/signup/', {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'JOHN@test.com',
            'password1': PASSWORD,
            'password2': PASSWORD,
        }, content_type='application/json')

        assert response.status_code == 400

    def test_user_login_and_logout(self, client):
        User.objects.create_user(username='john@test.com', email='john@test.com', password=PASSWORD)

        response = client.post('/api/auth/login/', {
            'email': 'JOHN@test.com',
            'password': PASSWORD,
        }, content_type='application/json')

        assert response.status_code == 200
        assert response.data['user']['email'] == 'john@test.com'

        me = client.get('/api/auth/user/')
        assert me.status_code == 200

        logged_out = client.post('/api/auth/logout/', content_type='application/json')
        assert logged_out.status_code == 200
        assert client.get('/api/auth/user/').status_code == 403

    def test_login_rejects_bad_password(self, client):
        User.objects.create_user(username='john@test.com', email='john@test.com', password=PASSWORD)
        response = client.post('/api/auth/login/', {
            'email': 'john@test.com',
            'password': 'wrong-password',
        }, content_type='application/json')
        assert response.status_code == 401

    def test_protected_endpoint(self, client):
        response = client.get('/api/auth/user/')
        assert response.status_code == 403

    def test_health_and_config(self, client):
        health = client.get('/api/health/')
        assert health.status_code == 200
        assert health.data['status'] == 'ok'
        assert health.data['payment_mode'] == 'sandbox'

        config = client.get('/api/config/')
        assert config.status_code == 200
        assert config.data['charge_mode'] == 'sandbox'
        assert config.data['demo_login']['email'] == 'demo@paygate.dev'
