from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.utils import timezone

from .models import Link
from analytics.models import Click
from links.utils import RESERVED_IDENTIFIERS


def redirect_link(request, identifier: str):
    """
    Redirect endpoint: GET /<identifier>

    identifier can be either:
    - short_code
    - custom_alias

    Behavior:
    - If identifier is reserved (e.g. 'admin'), return 404.
    - Lookup Link by short_code or custom_alias.
    - If not found, or expired / inactive, return 404.
    - Otherwise:
        - Record Click event.
        - Increment click_count.
        - Redirect to original_url.
    """
    if identifier.lower() in RESERVED_IDENTIFIERS:
        return HttpResponseNotFound("Not found.")

    link = (
        Link.objects.filter(short_code=identifier).first()
        or Link.objects.filter(custom_alias=identifier).first()
    )

    if link is None:
        return HttpResponseNotFound("Short link not found.")

    if link.is_expired():
        return HttpResponseNotFound("This link has expired or is inactive.")

    ip = request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    now = timezone.now()

    Click.objects.create(
        url=link,
        clicked_at=now,
        ip_address=ip,
        user_agent=user_agent,
        # country, city, device_type, browser will be filled later via analytics pipeline
    )

    link.click_count = link.click_count + 1
    link.save(update_fields=['click_count'])

    # Redirect to original URL
    return HttpResponseRedirect(link.original_url)