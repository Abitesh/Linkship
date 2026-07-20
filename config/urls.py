from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from links.views import redirect_link 

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    # 1. Admin Panel
    path('admin/', admin.site.urls),

    # 2. Web Frontend
    path('', include('links.urls')),       # Sends '' and 'about/' to links app
    path('users/', include('users.urls')), # Sends 'register/', 'login/', etc. to users app

    # 3. Password Reset (Web)
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password_reset_complete'),

    # 4. API Backend 
    path('api/links/', include('links.api_urls')),  
    path('api/auth/jwt/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/jwt/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # 5. Short Link Redirect 
    path('<str:identifier>/', redirect_link, name='redirect_link'),

    # OpenAPI Schema Generation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # Interactive Swagger UI: http://127.0.0.1:8000/api/docs/
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # Alternative Redoc UI: http://127.0.0.1:8000/api/redoc/
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)