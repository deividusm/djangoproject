from django.urls import path
from mysite.views import aprende, recicla  # Asegúrate de que las vistas sean correctas

urlpatterns = [
    path('', recicla, name='recicla'),
    path('aprende/', aprende, name='aprende'),
]
