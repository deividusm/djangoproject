from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from mysite.views import hub  # <-- Nota: He quitado 'ranking' de aquí
from .views import SubirImagenView 

urlpatterns = [
    path('', lambda r: redirect('account_login'), name='home'), 
    
    path('hub/', hub, name='hub'),
    
    # Esta línea es la que DEBES ELIMINAR:
    # path('ranking/', ranking, name='ranking'), 
    
    path('admin/', admin.site.urls),
    
    path('accounts/', include('allauth.urls')),

    path('verificar_mobilenet/', SubirImagenView.as_view(), name='verificar_mobilenet'),
    
    # Esta línea es la CORRECTA y debe quedarse. 
    # Gestionará /ranking/, /ranking/saldo/, etc.
    path('ranking/', include('ranking.urls', namespace='ranking')), 
]

