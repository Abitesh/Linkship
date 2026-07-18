from django.conf import settings
from django.db import models
from django.utils import timezone

class Link(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='links',
        help_text='User who created this short link.'
    )

    original_url = models.URLField(
        max_length=2048,
        help_text='The long URL that will be shortened.'
    )

    # Our generated short code (Base62)
    short_code = models.CharField(
    max_length=16,
    unique=True,
    db_index=True,
    null=True,
    blank=True,
    help_text='Automatically generated Base62 short code.'
    )

    # Optional custom alias chosen by user
    custom_alias = models.CharField(
        max_length=64,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        help_text='Human-friendly custom alias, e.g. "my-link".'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When set, this link stops working after this time.'
    )

    is_active = models.BooleanField(
        default=True,
        help_text='Soft delete / disable flag.'
    )

    click_count = models.PositiveIntegerField(
        default=0,
        help_text='Cached total number of clicks for quick access.'
    )

    qr_code_image = models.ImageField(
        upload_to='qr_codes/',
        null=True,
        blank=True,
        help_text='Generated QR code image pointing to this short link.'
    )

    class Meta:
        ordering = ['-created_at']  # Newest links first
        indexes = [
            models.Index(fields=['short_code']),
            models.Index(fields=['custom_alias']),
            models.Index(fields=['owner', 'created_at']),
        ]

    def __str__(self):
        identifier = self.custom_alias or self.short_code or '(pending)'
        return f'{identifier} -> {self.original_url}'

    def is_expired(self) -> bool:
        """
        Returns True if the link should no longer be usable.
        A link is considered expired if:
          - is_active is False, or
          - expires_at is set and current time is past expires_at.
        """
        if not self.is_active:
            return True

        if self.expires_at is None:
            return False

        now = timezone.now()
        return now >= self.expires_at

    def get_full_short_url(self) -> str:
        base = getattr(settings, 'SHORT_BASE_URL', None)
        code_or_alias = self.custom_alias or self.short_code

        if base and code_or_alias:
            return f'{base.rstrip("/")}/{code_or_alias}'
        elif code_or_alias:
            return f'/{code_or_alias}'
        return ''