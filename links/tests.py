from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.test import override_settings
# Adjust import based on your exact model name

from .models import Link
User = get_user_model()

@override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}})
class LinkManagementTests(APITestCase):
    """
    Test suite for URL shortening logic, custom aliases, and redirects.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='linktester', 
            email='tester@test.com', 
            password='pw123'
        )
        self.create_url = '/api/urls/' # Adjust if your router path differs
        
    def test_create_short_url_authenticated(self):
        """Authenticated users should be able to create a short URL."""
        self.client.force_authenticate(user=self.user)
        payload = {'original_url': 'https://www.systemdesign.com'}
        
        response = self.client.post(self.create_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('short_code', response.data)

    def test_duplicate_custom_alias_fails(self):
        """System must reject a custom alias if it is already in the database."""
        self.client.force_authenticate(user=self.user)
        # Seed the database with a taken alias
        Link.objects.create(
            original_url='https://example.com', 
            short_code='mybrand', 
            owner=self.user
        )
        
        payload = {
            'original_url': 'https://anotherexample.com',
            'custom_alias': 'mybrand'
        }
        response = self.client.post(self.create_url, payload)
        
        # 400 Bad Request expected because validation should catch the collision
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_expired_url_redirect(self):
        """An expired URL should return a 410 Gone or custom error message."""
        past_time = timezone.now() - timedelta(days=1)
        expired_url = Link.objects.create(
            original_url='https://example.com',
            short_code='expired1',
            expires_at=past_time,
            owner=self.user
        )
        
        response = self.client.get(f'/{expired_url.short_code}/')
        
        # Depending on your implementation, this might be a 404 or a custom template.
        # Assuming a 404 or 410 for expired logic:
        self.assertIn(response.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_410_GONE])