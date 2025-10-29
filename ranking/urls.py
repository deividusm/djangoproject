# ranking/urls.py
from django.urls import path
from . import views

app_name = 'ranking'

urlpatterns = [
    path('', views.ranking_page, name='page'),
    path('saldo/', views.saldo, name='saldo'),
    path('compra/', views.compra, name='compra'),
    path('historial/', views.historial, name='historial'),
]
