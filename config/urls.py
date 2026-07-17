from django.contrib import admin
from django.urls import path, include

from links.views import redirect_link  # your redirect view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('links.api_urls')),  
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    path('<str:identifier>/', redirect_link, name='redirect_link'),
]