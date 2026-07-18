from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from links.views import redirect_link  # your redirect view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('links.api_urls')),  
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    path('api/', include('users.urls')),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('<str:identifier>/', redirect_link, name='redirect_link'),
]