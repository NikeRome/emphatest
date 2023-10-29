"""
URL configuration for test_emphasoft project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from hotel_1.views import (
    RoomListAPIView, 
    ReservationCreateAPIView, 
    UserRegistrationAPIView,
    user_profile
)



urlpatterns = [
    path('admin/', admin.site.urls),
    path('rooms/', RoomListAPIView.as_view(), name='room-list'),
    path('reservations/', ReservationCreateAPIView.as_view(), name='reservation-create'),
    path('register/', UserRegistrationAPIView.as_view(), name='user-register'),
    path('login/', auth_views.LoginView.as_view(template_name='hotel_1/login.html'), name='user-login'),
    path('logout/', auth_views.LogoutView.as_view(), name='user-logout'),
    path('accounts/profile/', user_profile, name='user-profile'),
]
