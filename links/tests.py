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
        self.create_url = '/api/links/urls/' # Adjust if your router path differs
        
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

from django.test import TestCase, override_settings
from django.utils import timezone
from datetime import timedelta

from django.core.cache import cache
from django.contrib.auth import get_user_model

from links.models import Link

User = get_user_model()


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }
)
class RedirectFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="rediruser",
            email="redir@example.com",
            password="pw123",
        )

    def test_basic_redirect(self):
        """Active link should return 302 to original_url."""
        link = Link.objects.create(
            owner=self.user,
            original_url="https://www.example.com",
            short_code="abc123",
            is_active=True,
        )

        response = self.client.get(f"/{link.short_code}/")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], link.original_url)

    def test_expired_link_returns_404(self):
        """Expired link should not redirect, should return 404."""
        past = timezone.now() - timedelta(days=1)
        link = Link.objects.create(
            owner=self.user,
            original_url="https://www.example.com",
            short_code="expired1",
            expires_at=past,
            is_active=True,
        )

        response = self.client.get(f"/{link.short_code}/")

        self.assertEqual(response.status_code, 404)

    def test_cache_is_used_for_redirect(self):
        """Second request should still succeed with cache enabled."""
        link = Link.objects.create(
            owner=self.user,
            original_url="https://www.example.com",
            short_code="cache1",
            is_active=True,
        )

        # First request populates the cache
        first = self.client.get(f"/{link.short_code}/")
        self.assertEqual(first.status_code, 302)

        # Clear database to simulate a failure
        Link.objects.all().delete()

        # Second request should hit cache and still work (depending on your logic)
        second = self.client.get("/cache1/")
        # If your view deletes cache on DB miss, this may be 404; adapt assertion to your behavior.
        # For now we assert it is either 302 or 404, not 500.
        self.assertIn(second.status_code, (302, 404))

from rest_framework.test import APIClient
from rest_framework import status


class QrEndpointTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="qruser",
            email="qr@example.com",
            password="pw123",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.link = Link.objects.create(
            owner=self.user,
            original_url="https://www.example.com",
            short_code="qr1",
            is_active=True,
        )
        # You may want to call generate_qr_for_link(self.link) here if not done automatically
        from links.qr_utils import generate_qr_for_link
        generate_qr_for_link(self.link)

    def test_qr_endpoint_returns_png(self):
        """GET /api/urls/{id}/qr/ should return a PNG file."""
        response = self.client.get(f"/api/links/urls/{self.link.id}/qr/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "image/png")
        self.assertIn("attachment;", response["Content-Disposition"])