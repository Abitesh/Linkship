from __future__ import annotations

from celery import shared_task
from django.utils import timezone

from analytics.models import Click
from links.models import Link
from analytics.utils import parse_user_agent, ip_to_location


@shared_task
def record_click_task(link_id: int, ip: str | None, raw_user_agent: str | None, clicked_at_iso: str | None):
    """
    Asynchronous task to record a click event with enrichment.

    - Loads Link by ID
    - Parses user agent into device_type, browser
    - Maps IP to country/city
    - Creates Click row
    - Optionally increments cached click_count (if you decide to)
    """
    try:
        link = Link.objects.get(id=link_id)
    except Link.DoesNotExist:
        return

    # Parse timestamp back from ISO if provided, otherwise use now
    clicked_at = timezone.now()
    if clicked_at_iso:
        try:
            clicked_at = timezone.datetime.fromisoformat(clicked_at_iso)
            if timezone.is_naive(clicked_at):
                clicked_at = timezone.make_aware(clicked_at)
        except Exception:
            clicked_at = timezone.now()

    ua_info = parse_user_agent(raw_user_agent or '')
    device_type = ua_info['device_type']
    browser = ua_info['browser']

    location = ip_to_location(ip or '')
    country = location['country']
    city = location['city']

    Click.objects.create(
        url=link,
        clicked_at=clicked_at,
        ip_address=ip or '',
        user_agent=raw_user_agent or '',
        country=country,
        city=city,
        device_type=device_type,
        browser=browser,
    )

    # OPTIONAL: if you want click_count to reflect async events too,
    # you could increment here instead of in the view.
    # For now we keep click_count tied to real redirect path only.