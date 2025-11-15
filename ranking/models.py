# Pega esto en tu models.py (y borra todo lo demás)

from django.db import models
from django.conf import settings # La forma correcta de referirse al usuario de Django

class Profile(models.Model):
    # Conectamos 1-a-1 con el usuario de Django (el de allauth)
    # Si borras un usuario, se borra su perfil.
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    
    # El puntaje total
    total_points = models.BigIntegerField(default=0)

    def __str__(self):
        return f"Perfil de {self.user.username}: {self.total_points} puntos"

class Task(models.Model):
    # Conectamos la tarea a un usuario
    # Si borras un usuario, se borran sus tareas.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    complete = models.BooleanField(default=False) # ¿Está completada?
    created = models.DateTimeField(auto_now_add=True) # Fecha de creación
    
    # ¡Importante! Los puntos que da esta tarea específica
    points = models.IntegerField(default=10) 

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['complete'] # Las tareas incompletas aparecen primero