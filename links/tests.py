"""
Comprehensive test suite for the Links app.
Tests URL creation, redirection, analytics access, and edge cases.
"""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Link

User = get_user_model()


class LinkAPITests(APITestCase):
    def setUp(self):
        """
        Runs before EVERY test.
        Sets up a test user and forces authentication.
        """
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com', 
            password='testpassword123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Clear cache before tests to prevent state leakage
        cache.clear()

        # We assume you registered URLViewSet with router as 'url'
        self.list_create_url = reverse('url-list')

    def test_create_short_url_success(self):
        """Test standard URL creation generates a short code."""
        data = {'original_url': 'https://www.google.com'}
        response = self.client.post(self.list_create_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('short_code', response.data)
        self.assertEqual(response.data['original_url'], 'https://www.google.com')
        self.assertEqual(response.data['click_count'], 0)

    def test_create_custom_alias_success(self):
        """Test URL creation with a valid custom alias."""
        data = {
            'original_url': 'https://www.github.com',
            'custom_alias': 'my-github'
        }
        response = self.client.post(self.list_create_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['custom_alias'], 'my-github')

    def test_create_duplicate_custom_alias_fails(self):
        """Test that using an already taken alias returns an error."""
        Link.objects.create(
            owner=self.user,
            original_url='https://example.com',
            custom_alias='taken-alias'
        )
        
        data = {
            'original_url': 'https://www.yahoo.com',
            'custom_alias': 'taken-alias'
        }
        response = self.client.post(self.list_create_url, data)
        
        # DRF ValidationError usually returns 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_creation_fails(self):
        """Test that anonymous users cannot hit the authenticated endpoint."""
        self.client.logout()  # Remove authentication
        data = {'original_url': 'https://www.google.com'}
        response = self.client.post(self.list_create_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LinkRedirectTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test2', password='pw')
        self.link = Link.objects.create(
            owner=self.user,
            original_url='https://www.python.org',
            short_code='py123'
        )
        cache.clear()

    def test_valid_redirect(self):
        """Test that hitting the short code redirects to the original URL."""
        # Assuming your redirect URL is mounted at the root /<identifier>
        response = self.client.get(f'/{self.link.short_code}')
        
        # 302 Found is expected for HttpResponseRedirect
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, self.link.original_url)
        
        # Verify click count increased in the database
        self.link.refresh_from_db()
        self.assertEqual(self.link.click_count, 1)

    def test_expired_link_returns_404(self):
        """Test that an expired link does not redirect."""
        expired_link = Link.objects.create(
            owner=self.user,
            original_url='https://www.expired.com',
            short_code='exp1',
            expires_at=timezone.now() - timedelta(days=1)  # Expired yesterday
        )
        
        response = self.client.get(f'/{expired_link.short_code}')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_short_code_returns_404(self):
        """Test that a non-existent short code safely 404s."""
        response = self.client.get('/doesnotexist')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class LinkAnalyticsTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='pw')
        self.other_user = User.objects.create_user(username='other', password='pw')
        self.link = Link.objects.create(
            owner=self.owner,
            original_url='https://www.django.com',
            short_code='dj1'
        )
        # detail-route in ViewSet: 'url-analytics' using the router
        self.analytics_url = reverse('url-analytics', kwargs={'pk': self.link.pk})
        cache.clear()

    def test_owner_can_access_analytics(self):
        """Test that the owner of the link gets a 200 OK."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.analytics_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_clicks', response.data)

    def test_non_owner_cannot_access_analytics(self):
        """Test that another authenticated user gets a 403 Forbidden."""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.analytics_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)