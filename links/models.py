from django.conf import settings
from django.db import models

class Link(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='links'
    )
    original_url = models.URLField(max_length=2048)
    short_code = models.CharField(max_length=16, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    click_count = models.PositiveIntegerField(default=0)

    # Optional: soft-delete flag, etc.
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.short_code} -> {self.original_url}'