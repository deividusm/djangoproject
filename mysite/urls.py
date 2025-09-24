from django.urls import path, include
from mysite.views import aprende, recicla  # Asegúrate de que las vistas sean correctas

urlpatterns = [
    # Ruta principal, llama a la vista 'recicla'
    path('', recicla, name='recicla'),

    # Ruta para la página de aprendizaje, llama a la vista 'aprende'
    path('aprende/', aprende, name='aprende'),

    # Rutas relacionadas con autenticación de Google usando django-allauth
    path('accounts/', include('allauth.urls')),  # Maneja login, logout, signup, etc.
]
