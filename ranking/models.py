# ranking/models.py
from django.db import models
from django.conf import settings
import uuid

class Categorias(models.Model):
    id = models.BigAutoField(primary_key=True)
    Nombre_categoria = models.TextField(blank=True, null=True)
    Puntos_Asignados = models.BigIntegerField(default=0)

    class Meta:
        db_table = 'Categorias'
        managed = False  # <-- importante

class Ranking(models.Model):
    user_id = models.UUIDField(primary_key=True)
    puntos_totales = models.BigIntegerField(default=0)

    class Meta:
        db_table = 'ranking'
        managed = False  # <-- importante

class ImagenesUsuario(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    url_imagen = models.TextField(blank=True, null=True)
    user_id = models.UUIDField()
    categoria_id = models.BigIntegerField()

    class Meta:
        db_table = 'imagenes usuario'
        managed = False  # <-- importante


# PERFIL local para mapear usuario Django -> UUID en Supabase
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    supabase_user_id = models.UUIDField(default=uuid.uuid4, unique=True)

    def __str__(self):
        return f"{self.user} ({self.supabase_user_id})"
