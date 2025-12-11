import pytest
from django.contrib.auth.models import User


@pytest.mark.django_db
class TestAuthentication:
    
    def test_user_signup(self, client):
        response = client.post('/api/auth/signup/', {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@test.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }, content_type='application/json')
        
        assert response.status_code == 201
        assert User.objects.filter(email='john@test.com').exists()
    
    def test_user_login(self, client):
        User.objects.create_user(
            username='john@test.com',
            email='john@test.com',
            password='testpass123'
        )
        
        # Login
        response = client.post('/api/auth/login/', {
            'email': 'john@test.com',
            'password': 'testpass123'
        }, content_type='application/json')
        
        assert response.status_code == 200
        assert response.data['message'] == 'Login successful.'
    
    def test_protected_endpoint(self, client):
        response = client.get('/api/auth/user/')
        
        assert response.status_code == 403
