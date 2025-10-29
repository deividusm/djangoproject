# ranking/views.py

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, redirect  # <--- Importar redirect
from django.views import View
from django.views.decorators.http import require_POST
from django.db import transaction
from .models import Profile
from mysite.supabase_client import get_supabase_server
from .image_validator import es_imagen_relevante
import uuid  # <--- Importar para nombres de archivo únicos
from django.contrib import messages  # <--- Importar para mejores mensajes

# ... (tus otras vistas: hub, ranking, comojugar, saldo, historial, compra) ...
# ... (no cambian) ...

@login_required 
def ranking_page(request):
    """
    Vista que maneja la solicitud GET para la página principal del ranking.
    """
    # En esta vista no necesitas lógica compleja, solo renderizar el template.
    return render(request, 'ranking/ranking.html', {})

@login_required # Es buena práctica proteger las APIs de datos
def saldo(request):
    """
    Vista API que retorna el ranking de jugadores y el saldo del usuario actual.
    """
    if request.method != 'GET':
        # Esta vista solo debería aceptar peticiones GET de fetch
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        sb = get_supabase_server()
        
        # 1. Obtener los datos del ranking (Supabase)
        # Asumimos que tu tabla 'ranking' contiene 'user_id', 'username' y 'points'
        ranking_res = sb.table('ranking').select('username', 'points') \
                                         .order('points', desc=True) \
                                         .execute()
        
        # 2. Obtener el saldo del usuario actual
        # Asumimos que el profile del usuario autenticado tiene el supa_user_id
        current_user_id = str(request.user.profile.supabase_user_id)
        
        user_balance_res = sb.table('ranking').select('points') \
                                              .eq('user_id', current_user_id) \
                                              .single().execute()
        
        current_balance = user_balance_res.data.get('points') if user_balance_res.data else 0

        # 3. Formato de respuesta para el JavaScript
        data = {
            'balance': current_balance,
            'players': ranking_res.data or [] # Lista de todos los jugadores y sus puntos
        }

        return JsonResponse(data)
        
    except Exception as e:
        print(f"Error al obtener datos de Supabase para el ranking: {e}")
        return JsonResponse({'error': 'Error interno al obtener datos del ranking.'}, status=500)
    
# ranking/views.py - FUNCIÓN COMPRA CORREGIDA

@require_POST
@login_required
@transaction.atomic
def compra(request):
    """
    Procesa la solicitud de compra, resta puntos al usuario y registra la acción.
    """
    # 1. Definimos la URL de fallback (página de error/reintento)
    # Reemplaza 'pagina_anterior_o_hub' con una URL válida de nivel de proyecto
    FALLBACK_URL = 'verificar_mobilenet' 
    
    try:
        # 1. Obtener datos del formulario
        item_id = request.POST.get('item_id') 
        
        if not item_id:
            messages.error(request, "Error: Debes seleccionar un artículo para comprar.")
            return redirect(FALLBACK_URL) # <-- Corregido
            
        sb = get_supabase_server()
        supa_user_id = str(request.user.profile.supabase_user_id)

        # 2. Buscar el costo del artículo en la BD
        item_res = sb.table('Items_Tienda').select('Costo', 'Nombre') \
                                          .eq('id', item_id) \
                                          .single().execute()

        if not item_res.data:
            messages.error(request, "Artículo no encontrado en la tienda.")
            return redirect(FALLBACK_URL) # <-- Corregido

        costo = item_res.data.get('Costo')
        nombre_item = item_res.data.get('Nombre')
        
        # Lógica para verificar si el usuario tiene puntos suficientes (IRÍA AQUÍ)
        # ... 
        
        # 3. Registrar la resta de puntos (Delta negativo)
        payload_ledger = {
            'user_id': supa_user_id, 
            'delta': -costo,  # <-- Negativo porque es una resta
            'reason': f'Compra: {nombre_item}'
        }
        sb.table('points_ledger').insert(payload_ledger).execute()

        # 4. Registrar la compra del artículo (en otra tabla si es necesario)
        # ...

        messages.success(request, f"¡Compra exitosa! Se restaron {costo} puntos por {nombre_item}.")
        return redirect('ranking:ranking_index') # <-- Redirección correcta con NAMESPACE
        
    except Exception as e:
        messages.error(request, f"Error al procesar la compra: {e}")
        return redirect(FALLBACK_URL) # <-- Corregido
    
@login_required 
def historial(request):
    """
    Vista que recupera el historial de transacciones (ledger) y acciones del usuario 
    desde Supabase y renderiza la plantilla para mostrarlo.
    """
    user_actions = []
    
    try:
        sb = get_supabase_server()
        supa_user_id = str(request.user.profile.supabase_user_id)

        # 1. Recuperar datos del 'ledger' (registro de puntos ganados/gastados)
        ledger_res = sb.table('points_ledger').select('*') \
                                              .eq('user_id', supa_user_id) \
                                              .order('created_at', desc=True) \
                                              .execute()
        
        # 2. Combinar los resultados o pasarlos directamente al contexto
        user_actions = ledger_res.data
        
    except Exception as e:
        # En caso de error de conexión o consulta
        print(f"Error al obtener el historial de Supabase: {e}")
        # Puedes añadir un mensaje de error a la plantilla si lo deseas
        
    context = {
        'historial_acciones': user_actions
    }
    
    # 3. Renderiza el template 'historial.html' (Asegúrate de que este archivo exista)
    return render(request, 'ranking/historial.html', context)

# Vista para mostrar el formulario de verificación de imagen
class VerificarMobileNetView(View):
    def get(self, request):
        # Es una buena práctica pasar las categorías desde la BD al template
        # para que el <select> sea dinámico, pero lo dejaremos simple por ahora.
        return render(request, 'verificar_mobilenet.html')

# Vista para manejar la subida y verificación de la imagen
class SubirImagenView(View):
    
    def get(self, request):
        # Muestra el formulario de subida de imagen
        return render(request, 'verificar_mobilenet.html')

    @transaction.atomic # Usar transacción de Django por si acaso
    def post(self, request):
        
        # 1. Obtiene los datos del formulario
        archivo = request.FILES.get('imagen_subida')
        categoria_nombre = request.POST.get('categoria') # Ej: "organicos", "papel"

        if not archivo or not categoria_nombre:
            messages.error(request, "Error: Debes subir una imagen Y seleccionar una categoría.")
            return redirect('verificar_mobilenet') # Redirige a la misma pág.

        # 2. Pasa la imagen al validador
        es_valida = es_imagen_relevante(archivo)

        # 3. Responde si la imagen NO es válida
        if not es_valida:
            resultado = "¡Imagen rechazada! ❌ No parece ser una planta o basurero."
            messages.warning(request, resultado)
            # Volvemos a renderizar para mostrar el mensaje de error
            return render(request, 'verificar_mobilenet.html', {'resultado': resultado})

        # ---
        # 4. ¡LA IMAGEN ES VÁLIDA! AQUÍ EMPIEZA LA LÓGICA DE PUNTOS
        # ---
        try:
            sb = get_supabase_server()
            supa_user_id = str(request.user.profile.supabase_user_id)

            # 5. Buscar cuántos puntos vale la categoría seleccionada
            cat_res = sb.table('Categorias').select('id', 'Puntos_Asignados') \
                                          .eq('Nombre_categoria', categoria_nombre) \
                                          .single().execute()

            if not cat_res.data:
                messages.error(request, f"Error: Categoría '{categoria_nombre}' no encontrada en la base de datos.")
                return redirect('verificar_mobilenet')

            puntos_a_sumar = cat_res.data.get('Puntos_Asignados')
            categoria_db_id = cat_res.data.get('id')

            if puntos_a_sumar is None or puntos_a_sumar <= 0:
                messages.warning(request, f"La categoría '{categoria_nombre}' no tiene puntos asignados.")
                return redirect('verificar_mobilenet')
            
            # 6. (Recomendado) Subir la imagen a Supabase Storage
            # Asegúrate de tener un "bucket" en Supabase Storage (ej: 'imagenes_acciones')
            # y que sea público o tengas las políticas RLS correctas.
            
            # Rebobinamos el archivo por si el validador lo leyó
            archivo.seek(0) 
            # Creamos un path único
            file_path = f"public/{supa_user_id}/{uuid.uuid4()}-{archivo.name}"
            
            sb.storage.from_('imagenes_acciones').upload(  # <--- CAMBIA 'imagenes_acciones' por el nombre de tu bucket
                file=archivo.read(),
                path=file_path,
                file_options={"content-type": archivo.content_type}
            )
            
            # Obtener la URL pública
            public_url = sb.storage.from_('imagenes_acciones').get_public_url(file_path) # <--- CAMBIA 'imagenes_acciones'

        except Exception as e:
            messages.error(request, f"Error al subir la imagen a Supabase Storage: {e}")
            return redirect('verificar_mobilenet')

        # 7. Asignar los puntos y registrar la acción
        try:
            # Insertar en 'points_ledger' (igual que en tu vista 'compra')
            # Asumimos que un trigger en Supabase actualizará la tabla 'ranking'
            payload_ledger = {
                'user_id': supa_user_id, 
                'delta': puntos_a_sumar, 
                'reason': f'Acción: {categoria_nombre}'
            }
            sb.table('points_ledger').insert(payload_ledger).execute()

            # (Recomendado) Registrar la imagen en tu tabla 'imagenes usuario'
            log_payload = {
                'user_id': supa_user_id,
                'url_imagen': public_url,
                'categoria_id': categoria_db_id
                # 'descripcion': request.POST.get('descripcion', '') # También puedes guardar la descripción
            }
            sb.table('imagenes usuario').insert(log_payload).execute()

        except Exception as e:
            messages.error(request, f"Error al registrar los puntos en la base de datos: {e}")
            # Aquí podrías añadir lógica para borrar la imagen de Storage si falla la BD (rollback)
            return redirect('verificar_mobilenet')

        # 8. ¡Éxito! Mostrar mensaje y redirigir
        resultado_exito = f"¡IMAGEN ACEPTADA! ✅ Has ganado {puntos_a_sumar} puntos."
        messages.success(request, resultado_exito)
        
        # Redirigimos para evitar que el usuario reenvíe el formulario si recarga la página
        return redirect('verificar_mobilenet')
