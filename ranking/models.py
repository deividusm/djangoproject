from django.db import models
from django.conf import settings # Para conectar al usuario de Django

# 1. El modelo para la tabla "Categorias"
# (Este modelo está bien, no necesita cambios)
class Categorias(models.Model):
    id = models.BigAutoField(primary_key=True)
    Nombre_categoria = models.TextField(blank=True, null=True)
    Puntos_Asignados = models.BigIntegerField(default=0)

    class Meta:
        db_table = 'Categorias' 

# 2. El modelo para la tabla "ranking" (MODIFICADO)
class Ranking(models.Model):
    # ¡CAMBIO!
    # Conectamos esto al usuario de Django como llave primaria.
    # OneToOneField asegura que cada usuario solo tenga UNA fila de ranking.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        primary_key=True
    )
    
    puntos_totales = models.BigIntegerField(default=0)

    class Meta:
        db_table = 'ranking'

# 3. El modelo para la tabla "imagenes usuario" (MODIFICADO)
class ImagenesUsuario(models.Model):
    id = models.AutoField(primary_key=True) #AutoField para int4
    created_at = models.DateTimeField(auto_now_add=True)
    url_imagen = models.TextField(blank=True, null=True)
    
    # ¡CAMBIO!
    # Conexión (Llave Foránea) al usuario de auth de Django.
    # Un usuario puede tener MUCHAS imágenes.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    
    # ¡CAMBIO!
    # Conexión (Llave Foránea) a la tabla Categorias.
    # SET_NULL significa que si borras una categoría, la imagen no se borra.
    categoria = models.ForeignKey(
        Categorias, 
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        db_table = 'imagenes usuario'

#
# Ya no necesitamos los campos 'user_id = models.UUIDField()'
# ni 'categoria_id = models.BigIntegerField()'
#