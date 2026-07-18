from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='links-home'),
    path('about/', views.about, name='links-about'),
]