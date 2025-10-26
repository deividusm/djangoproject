from django.urls import path, include
from django.shortcuts import redirect
from mysite.views import hub
from django.contrib import admin
from .views import SubirImagenView  # Solo importa SubirImagenView

urlpatterns = [
    path('', lambda r: redirect('account_login'), name='home'),  # Redirige al login si no está logueado
    path('hub/', hub, name='hub'),                                # Página principal, requiere login
    path('accounts/', include('allauth.urls')),                   # Autenticación de usuarios
    path('admin/', admin.site.urls),                              # Admin de Django
    path('verificar_mobilenet/', SubirImagenView.as_view(), name='verificar_mobilenet'),  # Solo una vista para subir y verificar la imagen
]
