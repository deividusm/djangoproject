# ranking/urls.py
from django.urls import path
from .views import (
    hub,
    ranking,
    comojugar,
    mapapuntos,
    SubirImagenView,
    task_validate,
)

urlpatterns = [
    # Home → menú principal (hub.html)
    path('', hub, name='home'),

    # Links del menú
    path('comojugar/', comojugar, name='comojugar'),
    path('ranking/', ranking, name='ranking'),
    path('mapapuntos/', mapapuntos, name='mapapuntos'),

    # Página principal de juego / subida de acciones
    path('verificar_mobilenet/', SubirImagenView.as_view(), name='verificar_mobilenet'),

    # Endpoint que usa el formulario del ranking para validar una Task concreta
    path('tarea/<int:task_id>/validar/', task_validate, name='task-validate'),
]
