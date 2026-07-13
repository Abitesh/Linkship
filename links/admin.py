from django.contrib import admin
from .models import Link

@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ('short_code', 'owner', 'original_url', 'created_at', 'is_active', 'click_count')
    list_filter = ('is_active', 'created_at')
    search_fields = ('short_code', 'original_url', 'owner__username')