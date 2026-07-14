from django.db import transaction
from django.db.models import Q

from .models import Link
from .utils import encode_base62


def identifier_exists(value: str, exclude_link_id: int | None = None) -> bool:
    queryset = Link.objects.all()

    if exclude_link_id is not None:
        queryset = queryset.exclude(id=exclude_link_id)

    return queryset.filter(
        Q(short_code=value) | Q(custom_alias=value)
    ).exists()

def build_unique_short_code(link_id: int, max_attempts: int = 5) -> str:
    """
    Generate a collision-safe short code from the numeric link ID.

    Normal case:
        encode_base62(link_id) is already unique.

    Fallback case:
        If conflict exists (because of alias/code overlap), append a suffix.
    """
    base_code = encode_base62(link_id)

    if not identifier_exists(base_code):
        return base_code

    for attempt in range(1, max_attempts + 1):
        candidate = f"{base_code}{attempt}"
        if not identifier_exists(candidate):
            return candidate

    raise ValueError("Unable to generate a unique short code after retries.")

def validate_custom_alias(alias: str) -> str:
    """
    Normalize and validate a user-provided alias.
    """
    alias = alias.strip()

    if not alias:
        raise ValueError("Custom alias cannot be empty.")

    if " " in alias:
        raise ValueError("Custom alias cannot contain spaces.")

    if identifier_exists(alias):
        raise ValueError("This alias is already in use.")

    return alias

def create_short_link(*, owner, original_url: str, custom_alias: str | None = None, expires_at=None) -> Link:
    """
    Create a new short link safely.

    Handles:
    - optional custom alias
    - unique generated short code
    - collision checks
    """
    with transaction.atomic():
        normalized_alias = None

        if custom_alias:
            normalized_alias = validate_custom_alias(custom_alias)

        link = Link.objects.create(
            owner=owner,
            original_url=original_url,
            custom_alias=normalized_alias,
            expires_at=expires_at,
        )

        if not normalized_alias:
            link.short_code = build_unique_short_code(link.id)
            link.save(update_fields=['short_code'])

        return link