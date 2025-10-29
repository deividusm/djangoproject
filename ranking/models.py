from django.db import models
from django.conf import settings # Para conectar al usuario de Django

# 1. El modelo para la tabla "Categorias"
class Categorias(models.Model):
    # OJO: Django crea un 'id' (PK) automáticamente. 
    # Para que coincida con tu SQL, definimos que el 'id' es 'bigint'
    id = models.BigAutoField(primary_key=True)
    Nombre_categoria = models.TextField(blank=True, null=True)
    Puntos_Asignados = models.BigIntegerField(default=0)

    class Meta:
        # Le dice a Django el nombre exacto de la tabla en Supabase
        db_table = 'Categorias' 

# 2. El modelo para la tabla "ranking"
class Ranking(models.Model):
    # Usamos el 'user_id' (uuid) como la Llave Primaria
    user_id = models.UUIDField(primary_key=True) 
    puntos_totales = models.BigIntegerField(default=0)

    class Meta:
        db_table = 'ranking'

# 3. El modelo para la tabla "imagenes usuario"
class ImagenesUsuario(models.Model):
    id = models.AutoField(primary_key=True) #AutoField para int4
    created_at = models.DateTimeField(auto_now_add=True)
    url_imagen = models.TextField(blank=True, null=True)
    
    # Conexión (Llave Foránea) al usuario de auth
    user_id = models.UUIDField() 
    
    # Conexión (Llave Foránea) a la tabla Categorias
    categoria_id = models.BigIntegerField()

    class Meta:
        db_table = 'imagenes usuario'
        # Nota: Los nombres de tus columnas "user-id" y "categoria_id" 
        # deben coincidir aquí. Si usaste guion bajo, cámbialos.
        # ej: user_id = models.UUIDField(db_column='user-id')


# Create your models here.
