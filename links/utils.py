import re
from urllib.parse import urlparse

from django.db.models import Q

from .models import Link

from django.core.cache import cache

BASE62_ALPHABET = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

from urllib.parse import urlparse
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

def validate_original_url(url: str) -> str:
    """
    Validates the URL format and prevents malicious/internal routing.
    """
    # 1. Basic format validation (Forces HTTP/HTTPS, blocks javascript: or file: schemes)
    validator = URLValidator(schemes=['http', 'https'])
    try:
        validator(url)
    except ValidationError:
        raise ValueError("Invalid URL format. Must start with http:// or https://")

    # 2. Parse the URL to inspect the domain
    parsed = urlparse(url)
    hostname = parsed.hostname.lower() if parsed.hostname else ''

    # 3. Security: Prevent SSRF (Server-Side Request Forgery)
    forbidden_hosts = [
        'localhost',
        '127.0.0.1',
        '0.0.0.0',
        '[::1]',
    ]
    # Block loopback and standard private IP ranges
    if (hostname in forbidden_hosts or 
        hostname.startswith('192.168.') or 
        hostname.startswith('10.') or
        hostname.startswith('172.')):
        raise ValueError("Internal, private, or local URLs are strictly forbidden.")

    # 4. Security: Prevent recursive shortening (Loop prevention)
    # Replace with your actual live domain to prevent infinite redirect loops
    if 'linkship-production.up.railway.app' in hostname:
        raise ValueError("Recursive shortening is not allowed. You cannot shorten a Linkship URL.")

    return url

def encode_base62(number: int) -> str:
    """
    Convert a non-negative integer into a Base62 string.

    Used to turn the numeric primary key of Link into a short_code.
    """
    if number < 0:
        raise ValueError('Number must be non-negative')

    if number == 0:
        return BASE62_ALPHABET[0]

    base = len(BASE62_ALPHABET)
    digits = []

    while number > 0:
        number, rem = divmod(number, base)
        digits.append(BASE62_ALPHABET[rem])

    return ''.join(reversed(digits))


def decode_base62(code: str) -> int:
    """
    Convert a Base62 string back into an integer.
    Mostly useful for debugging or future features.
    """
    base = len(BASE62_ALPHABET)
    value = 0

    for char in code:
        index = BASE62_ALPHABET.index(char)
        value = value * base + index

    return value


def identifier_exists(value: str, exclude_link_id: int | None = None) -> bool:
    """
    Check whether a public identifier (short_code or custom_alias)
    is already used by any Link.

    This protects the namespace of /<identifier> so we don't have
    ambiguous redirects.
    """
    queryset = Link.objects.all()

    if exclude_link_id is not None:
        queryset = queryset.exclude(id=exclude_link_id)

    return queryset.filter(
        Q(short_code=value) | Q(custom_alias=value)
    ).exists()


RESERVED_IDENTIFIERS = {
    'admin',
    'api',
    'login',
    'logout',
    'register',
    'signup',
    'docs',
    'static',
    'media',
}


ALIAS_PATTERN = re.compile(r'^[A-Za-z0-9_-]+$')


def validate_custom_alias(alias: str) -> str:
    """
    Normalize and validate a user-provided alias.

    Rules:
    - Trim whitespace.
    - Must match [A-Za-z0-9_-]+.
    - Must not be reserved.
    - Must not conflict with existing short_code or custom_alias.
    """
    alias = alias.strip()

    if not alias:
        raise ValueError("Custom alias cannot be empty.")

    if not ALIAS_PATTERN.match(alias):
        raise ValueError("Alias must be alphanumeric and may include '-' or '_' only.")

    if alias.lower() in RESERVED_IDENTIFIERS:
        raise ValueError("This alias is reserved and cannot be used.")

    if identifier_exists(alias):
        raise ValueError("This alias is already in use.")

    return alias


def validate_original_url(url: str) -> str:
    """
    Basic URL validation and malicious check.

    Rules:
    - Must have http or https scheme.
    - Must have a netloc (domain).
    - Reject obvious dangerous schemes (javascript:, data:, file:, etc.).
    """
    url = url.strip()

    if not url:
        raise ValueError("URL cannot be empty.")

    parsed = urlparse(url)

    if parsed.scheme not in ('http', 'https'):
        raise ValueError("URL must start with http:// or https://")

    if not parsed.netloc:
        raise ValueError("URL must have a domain.")

    # Basic malicious scheme check (we already filter non-http(s))
    # Additional blacklist can be added here (e.g., known bad domains).

    return url


def generate_short_code(link_id: int, max_attempts: int = 5) -> str:
    """
    Generate a collision-safe short code from the numeric link ID.

    Normal case:
        Base62(link_id) is unique.

    Fallback:
        If collision detected, append a numeric suffix until unique
        or raise after max_attempts.
    """
    base_code = encode_base62(link_id)

    if not identifier_exists(base_code):
        return base_code

    for attempt in range(1, max_attempts + 1):
        candidate = f'{base_code}{attempt}'
        if not identifier_exists(candidate):
            return candidate

    raise ValueError('Unable to generate a unique short code after multiple attempts.')




REDIRECT_CACHE_TTL = 60 * 60  # 1 hour


def make_redirect_cache_key(identifier: str) -> str:
    return f'link_redirect:{identifier}'