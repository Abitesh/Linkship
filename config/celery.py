from __future__ import absolute_import, unicode_literals

import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'linksnip.settings')

app = Celery('linksnip')

# Read CELERY_* settings from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks.py in all installed apps
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')