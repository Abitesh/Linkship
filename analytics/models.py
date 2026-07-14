from django.db import models
from django.utils import timezone
from links.models import Link


class Click(models.Model):
    url = models.ForeignKey(
        Link,
        on_delete=models.CASCADE,
        related_name='clicks',
        help_text='The short link that was clicked.'
    )

    clicked_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='Timestamp when the click occurred.'
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text='Visitor IP address (IPv4 or IPv6).'
    )

    user_agent = models.TextField(
        null=True,
        blank=True,
        help_text='Raw user agent string of the client.'
    )

    country = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text='Geolocated country for the IP.'
    )

    city = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text='Geolocated city for the IP.'
    )

    device_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text='Device type classification (mobile, desktop, tablet).'
    )

    browser = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text='Browser family (Chrome, Firefox, Safari, etc.).'
    )

    class Meta:
        ordering = ['-clicked_at']
        indexes = [
            models.Index(fields=['url', 'clicked_at']),
            models.Index(fields=['country']),
            models.Index(fields=['city']),
        ]

    def __str__(self):
        return f'Click on {self.url} at {self.clicked_at.isoformat()}'