from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # HTML Web Routes
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    

    path('logout/', views.logout_view, name='logout'),


    # API Route 
    path('api/register/', views.RegisterView.as_view(), name='api-register'),
]