import os
import dj_database_url
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

# Database (Dynamically connects to Railway Postgres)
DATABASES = {
    'default': dj_database_url.config(default=os.environ.get('DATABASE_URL'))
}

# Redis and Caching (Dynamically connects to Railway Redis)
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
CELERY_BROKER_URL = REDIS_URL

# Static files handling via Whitenoise
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Safely inject whitenoise without overwriting the middleware imported from base.py
if 'whitenoise.middleware.WhiteNoiseMiddleware' not in MIDDLEWARE:
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')