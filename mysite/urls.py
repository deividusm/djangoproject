from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

# Importa TODAS las vistas desde el archivo views.py de la app principal (mysite)
from . import views 

urlpatterns = [
    # Redirige la raíz del sitio al login
    path('', lambda r: redirect('account_login'), name='home'), 
    
    # URL del panel principal
    path('hub/', views.hub, name='hub'),
    
    # URL de "Cómo Jugar" (Esta era la que faltaba)
    path('comojugar/', views.comojugar, name='comojugar'),
    
    # URL del admin de Django
    path('admin/', admin.site.urls),
    
    # URLs de autenticación (login, logout, signup)
    path('accounts/', include('allauth.urls')),

    # URL para la verificación de imágenes
    path('verificar_mobilenet/', views.SubirImagenView.as_view(), name='verificar_mobilenet'),
    
    # URL de "Puntos de Reciclaje"
    path('mapapuntos/', views.mapapuntos, name='mapapuntos'),

    # --- URLs DESACTIVADAS ---
    # Dejamos comentada la URL de ranking que daba error, como querías
    # path('ranking/', include('ranking.urls', namespace='ranking')), 
]