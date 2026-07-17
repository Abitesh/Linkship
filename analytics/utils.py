from user_agents import parse as parse_ua
import geoip2.database
from django.conf import settings


_geoip_reader = None

def parse_user_agent(ua_string: str) -> dict:
    """
    Parse a raw user agent string into structured info.

    Returns dict with device_type, browser, os.
    """
    if not ua_string:
        return {
            'device_type': 'unknown',
            'browser': 'unknown',
            'os': 'unknown',
        }

    ua = parse_ua(ua_string)

    # Determine device type
    if ua.is_mobile:
        device_type = 'mobile'
    elif ua.is_tablet:
        device_type = 'tablet'
    elif ua.is_pc:
        device_type = 'desktop'
    elif ua.is_bot:
        device_type = 'bot'
    else:
        device_type = 'unknown'

    browser_family = ua.browser.family or 'unknown'
    os_family = ua.os.family or 'unknown'

    return {
        'device_type': device_type,
        'browser': browser_family,
        'os': os_family,
    }

def get_geoip_reader():
    """
    Lazily initialize and cache the GeoIP2 database reader.

    Uses settings.GEOIP2_DB_PATH.
    """
    global _geoip_reader
    if _geoip_reader is None:
        db_path = getattr(settings, 'GEOIP2_DB_PATH', None)
        if not db_path:
            return None
        try:
            _geoip_reader = geoip2.database.Reader(str(db_path))
        except FileNotFoundError:
            _geoip_reader = None
    return _geoip_reader


def ip_to_location(ip_address: str) -> dict:
    """
    Map IP address to location data using GeoLite2 City.

    Returns dict with country, city.

    For private/localhost IPs (127.0.0.1, 10.x, 192.168.x) or
    missing DB, returns 'unknown' values.
    """
    if not ip_address:
        return {
            'country': 'unknown',
            'city': 'unknown',
        }

    # Simple check for localhost/private ranges
    if ip_address.startswith('127.') or ip_address.startswith('10.') or ip_address.startswith('192.168.'):
        return {
            'country': 'local',
            'city': 'local',
        }

    reader = get_geoip_reader()
    if reader is None:
        return {
            'country': 'unknown',
            'city': 'unknown',
        }

    try:
        response = reader.city(ip_address)
        country = response.country.names.get('en') or 'unknown'
        city = response.city.names.get('en') or 'unknown'
        return {
            'country': country,
            'city': city,
        }
    except Exception:
        # Any lookup error → unknown
        return {
            'country': 'unknown',
            'city': 'unknown',
        }
