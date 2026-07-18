from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.utils import timezone

from .models import Link
from analytics.models import Click
from links.utils import RESERVED_IDENTIFIERS
from .serializers import URLSerializer, URLCreateSerializer, URLListSerializer

from django.db.models import Count
from django.db.models.functions import TruncDate
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from django.http import FileResponse, Http404
from rest_framework import status

from analytics.utils import parse_user_agent, ip_to_location

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
     # Reserved identifiers check
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

    # Basic request metadata
    ip = request.META.get('REMOTE_ADDR')
    raw_user_agent = request.META.get('HTTP_USER_AGENT', '')
    now = timezone.now()

    # Parse user agent
    ua_info = parse_user_agent(raw_user_agent)
    device_type = ua_info['device_type']
    browser = ua_info['browser']
    # os = ua_info['os']  # we can store later if needed

    # GeoIP lookup
    location = ip_to_location(ip)
    country = location['country']
    city = location['city']

    # Record click with enriched data
    Click.objects.create(
        url=link,
        clicked_at=now,
        ip_address=ip,
        user_agent=raw_user_agent,
        country=country,
        city=city,
        device_type=device_type,
        browser=browser,
    )

    # Increment cached click_count
    link.click_count = link.click_count + 1
    link.save(update_fields=['click_count'])

    return HttpResponseRedirect(link.original_url)

class URLViewSet(viewsets.ModelViewSet):
    """
    REST API for short URLs.

    Endpoints:
    - GET    /api/urls/           → list (URLListSerializer)
    - POST   /api/urls/           → create (URLCreateSerializer)
    - GET    /api/urls/{id}/      → retrieve (URLSerializer)
    - PUT    /api/urls/{id}/      → update (URLSerializer)
    - PATCH  /api/urls/{id}/      → partial_update (URLSerializer)
    - DELETE /api/urls/{id}/      → destroy
    """
    queryset = Link.objects.select_related('owner').all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return URLListSerializer
        if self.action == 'create':
            return URLCreateSerializer
        return URLSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['get'], url_path='analytics')
    def analytics(self, request, pk=None):
        """
        Analytics endpoint for a single URL.

        GET /api/urls/{id}/analytics/

        Returns:
        - total_clicks
        - clicks_over_time (daily)
        - top_countries
        - top_devices
        - top_browsers
        """
        try:
            link = self.get_queryset().get(pk=pk)
        except Link.DoesNotExist:
            return Response({'detail': 'Link not found.'}, status=404)

        # Only allow owner to see analytics (you can relax this later if needed)
        if link.owner != request.user:
            return Response({'detail': 'Not allowed.'}, status=403)

        qs = Click.objects.filter(url=link)

        # Total clicks
        total_clicks = qs.count()

        # Clicks over time (daily counts)
        by_day = (
            qs.annotate(day=TruncDate('clicked_at'))
              .values('day')
              .annotate(count=Count('id'))
              .order_by('day')
        )

        # Top countries
        by_country = (
            qs.values('country')
              .annotate(count=Count('id'))
              .order_by('-count')
        )

        # Top devices
        by_device = (
            qs.values('device_type')
              .annotate(count=Count('id'))
              .order_by('-count')
        )

        # Top browsers
        by_browser = (
            qs.values('browser')
              .annotate(count=Count('id'))
              .order_by('-count')
        )

        data = {
            'total_clicks': total_clicks,
            'clicks_over_time': list(by_day),
            'top_countries': list(by_country),
            'top_devices': list(by_device),
            'top_browsers': list(by_browser),
        }
        return Response(data)
    
    queryset = Link.objects.select_related('owner').all()
    permission_classes = [permissions.IsAuthenticated]

    def qr(self, request, pk=None):
        """
        GET /api/urls/{id}/qr/

        Returns the QR code image file for this URL.

        - Requires authentication and ownership.
        - Sets Content-Disposition so browsers can download.
        """
        try:
            link = self.get_queryset().get(pk=pk)
        except Link.DoesNotExist:
            raise Http404("Link not found.")

        if link.owner != request.user:
            return Response({'detail': 'Not allowed.'}, status=status.HTTP_403_FORBIDDEN)

        if not link.qr_code_image:
            return Response({'detail': 'QR code not generated.'}, status=status.HTTP_404_NOT_FOUND)

        qr_file = link.qr_code_image.open('rb')
        response = FileResponse(qr_file, content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="link_{link.id}_qr.png"'
        return response
    
