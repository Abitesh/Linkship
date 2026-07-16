from django.contrib import admin
from django.urls import path, include

from links.views import redirect_link  # your redirect view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('links.api_urls')),  # /api/urls/ etc.
    # other api groups later...

    path('<str:identifier>/', redirect_link, name='redirect_link'),
]