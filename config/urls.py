from django.contrib import admin
from django.urls import path, include

from links.views import redirect_link

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('api/', include('api.urls')),  # future DRF APIs
    # ... other routes ...

    # Catch-all for short links: must be LAST because it matches any string
    path('<str:identifier>/', redirect_link, name='redirect_link'),
]