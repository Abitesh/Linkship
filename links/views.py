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

from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

from django.core.cache import cache
from links.utils import make_redirect_cache_key, REDIRECT_CACHE_TTL

from django.shortcuts import render

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

    cache_key = make_redirect_cache_key(identifier)
    cached = cache.get(cache_key)

    if cached:
        if cached.get('expired'):
            return HttpResponseNotFound("This link has expired or is inactive.")

        try:
            link = Link.objects.get(id=cached['link_id'])
        except Link.DoesNotExist:
            cache.delete(cache_key)
            return HttpResponseNotFound("Short link not found.")
    else:
        link = (
            Link.objects.filter(short_code=identifier).first()
            or Link.objects.filter(custom_alias=identifier).first()
        )

        if link is None:
            return HttpResponseNotFound("Short link not found.")

        cache.set(
            cache_key,
            {
                'link_id': link.id,
                'original_url': link.original_url,
                'expired': link.is_expired(),
            },
            REDIRECT_CACHE_TTL,
        )

    if link.is_expired():
        cache.set(
            cache_key,
            {
                'link_id': link.id,
                'original_url': link.original_url,
                'expired': True,
            },
            REDIRECT_CACHE_TTL,
        )
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
    
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filters the database so the dashboard only returns links 
        owned by the currently authenticated user.
        """
        return Link.objects.filter(owner=self.request.user).select_related('owner').order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'list':
            return URLListSerializer
        if self.action == 'create':
            return URLCreateSerializer
        return URLSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return URLListSerializer
        if self.action == 'create':
            return URLCreateSerializer
        return URLSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_throttles(self):
        # Apply throttling only for create action
        if self.action == 'create':
            return [UserRateThrottle(), AnonRateThrottle()]
        return []

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
            cache_key = f'link_analytics:{link.id}'
            cached_data = cache.get(cache_key)

            if cached_data is not None:
                return Response(cached_data)
            return Response({'detail': 'Not allowed.'}, status=403)
        

        try:
            link = self.get_queryset().get(pk=pk)
        except Link.DoesNotExist:
            return Response({'detail': 'Link not found.'}, status=404)

        if link.owner != request.user:
            return Response({'detail': 'Not allowed.'}, status=403)

        cache_key = f'link_analytics:{link.id}'
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

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

        cache.set(cache_key, data, 60 * 5)  # 5 minutes
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
    
    def perform_update(self, serializer):
        link = serializer.save()
        # Invalidate cache for short_code and custom_alias
        identifiers = []
        if link.short_code:
            identifiers.append(link.short_code)
        if link.custom_alias:
            identifiers.append(link.custom_alias)
        for ident in identifiers:
            cache.delete(make_redirect_cache_key(ident))

    def perform_destroy(self, instance):
        identifiers = []
        if instance.short_code:
            identifiers.append(instance.short_code)
        if instance.custom_alias:
            identifiers.append(instance.custom_alias)
        for ident in identifiers:
            cache.delete(make_redirect_cache_key(ident))
        instance.delete()
    

# HTML 
def home(request):
    """ Renders the main Linkship landing page """
    return render(request, 'links/home.html', {'title': 'Home'})

def about(request):
    """ Renders the About page """
    return render(request, 'links/about.html', {'title': 'About'})