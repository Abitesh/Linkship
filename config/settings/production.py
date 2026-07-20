import os
import dj_database_url
from .base import *

DEBUG = False
ALLOWED_HOSTS = ['*']

# Ensure these settings are present
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') 

# Database and Redis settings...
DATABASES = {'default': dj_database_url.config(default=os.environ.get('DATABASE_URL'))}
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"}
    }
}
CELERY_BROKER_URL = REDIS_URL

# Whitenoise is CRITICAL for production
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Ensure this is here
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'