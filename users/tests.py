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
        self.register_url = reverse('api-register') 
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

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model


User = get_user_model()

@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }
)
class JwtAuthTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="jwtuser",
            email="jwt@example.com",
            password="pw123",
        )
        self.client = APIClient()

    def test_obtain_jwt_and_access_protected_endpoint(self):
        """User should obtain JWT and use it to access /api/urls/."""
        # Adjust URL to your JWT login path
        login_url = "/api/auth/jwt/login/"

        response = self.client.post(
            login_url,
            {"username": "jwtuser", "password": "pw123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access = response.data.get("access")
        self.assertIsNotNone(access)

        # Now call a protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        urls_response = self.client.get("/api/links/urls/")
        # Depending on your router, adjust the path to /api/links/ if needed.
        self.assertIn(urls_response.status_code, (status.HTTP_200_OK, status.HTTP_204_NO_CONTENT))