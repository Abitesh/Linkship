from django.db import transaction

from .models import Link
from .utils import (
    validate_original_url,
    validate_custom_alias,
    generate_short_code,
)


def create_short_link(*, owner, original_url: str, custom_alias: str | None = None, expires_at=None) -> Link:
    """
    Create a new short link safely.

    Handles:
    - URL validation
    - optional custom alias validation
    - unique generated short code
    - collision checks
    """
    validated_url = validate_original_url(original_url)

    normalized_alias = None
    if custom_alias:
        normalized_alias = validate_custom_alias(custom_alias)

    with transaction.atomic():
        link = Link.objects.create(
            owner=owner,
            original_url=validated_url,
            custom_alias=normalized_alias,
            expires_at=expires_at,
        )

        if not normalized_alias:
            # Generate short_code from link.id and ensure uniqueness
            short_code = generate_short_code(link.id)
            link.short_code = short_code
            link.save(update_fields=['short_code'])

        return link