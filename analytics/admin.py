from django.contrib import admin
from .models import Click


@admin.register(Click)
class ClickAdmin(admin.ModelAdmin):
    list_display = (
        'url',
        'clicked_at',
        'ip_address',
        'country',
        'city',
        'device_type',
        'browser',
    )
    list_filter = ('country', 'city', 'device_type', 'browser')
    search_fields = ('url__short_code', 'url__custom_alias', 'ip_address', 'user_agent')