# ranking/models.py

from django.db import models
from django.conf import settings


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True
    )
    total_points = models.BigIntegerField(default=0)

    def __str__(self):
        return f"Perfil de {self.user.username} ({self.total_points} pts)"


class Task(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    complete = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    points = models.IntegerField(default=10)

    class Meta:
        ordering = ['complete', '-created']

    def __str__(self):
        return self.title


class ImagenesUsuario(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='imagenes_subidas'
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='imagenes'
    )
    imagen = models.ImageField(upload_to='evidencias/')
    puntos_otorgados = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.task.title} ({self.puntos_otorgados} pts)"
