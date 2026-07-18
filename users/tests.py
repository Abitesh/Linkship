from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import override_settings

User = get_user_model()

@override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}})
class AuthenticationTests(APITestCase):
    """
    Test suite for User Registration and JWT Authentication flows.
    """
    
    def setUp(self):
        # Reverse lookup ensures we don't hardcode URL strings
        self.register_url = reverse('auth_register') 
        self.valid_user_payload = {
            'username': 'testengineer',
            'email': 'engineer@example.com',
            'password': 'securepassword123'
        }

    def test_successful_user_registration(self):
        """Ensure a new user can register and receives JWT tokens."""
        response = self.client.post(self.register_url, self.valid_user_payload)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertEqual(User.objects.count(), 1)

    def test_duplicate_email_registration_fails(self):
        """Ensure the system prevents registration with an already existing email."""
        # Create user once
        self.client.post(self.register_url, self.valid_user_payload)
        # Attempt exact same registration
        response = self.client.post(self.register_url, self.valid_user_payload)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1) # Count should not increase