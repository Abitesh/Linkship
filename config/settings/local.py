from .base import *
import os
from pathlib import Path

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Path to GeoLite2 database for local/dev
GEOIP2_DB_PATH = BASE_DIR / 'geo' / 'GeoLite2-City.mmdb'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-ptarwm&mr68g#_z$x7roc4q9*z+nz@bb=d7g=t7^)3734&)f@b'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

SHORT_BASE_URL = 'http://127.0.0.1:8000'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'linksnip_db',
        'USER': 'linksnip_abitesh',
        'PASSWORD': 'Linksnip@1977',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
    }
}