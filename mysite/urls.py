from django.urls import path, include
from django.shortcuts import redirect
from mysite.views import hub
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('', lambda r: redirect('account_login'), name='home'),  # raíz → login
    path('hub/', hub, name='hub'),                                # menú real
    path('accounts/', include('allauth.urls')),                   # allauth
]

#urls.py
