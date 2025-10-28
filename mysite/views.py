from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views import View
from .image_validator import es_imagen_relevante  # Importa la función de validación de imagen

# Vista para el Hub (requiere estar logueado)
@login_required(login_url='account_login')
def hub(request):
    return render(request, 'hub.html')  # Hub se muestra solo si el usuario está logueado
@login_required(login_url='account_login')
def ranking(request):
    return render(request, 'ranking.html') 
@login_required(login_url='account_login')
def hub(request):
    # Aquí buscarías en tu base de datos...
    # (Por ahora, usamos datos de ejemplo)
    
    # Datos que irán al JavaScript
    contexto_js = {
        'me': {
            'name': request.user.username,
            'points': 150  # Deberías sacar esto de la base de datos
        },
        'photos': [
            # Deberías sacar esto de la base de datos
            {'data': '/media/fotos/mi_foto.jpg', 'catLabel': 'Plásticos', 'desc': 'Botellas de la semana'},
        ],
        'players': [
            # Deberías sacar esto de la base de datos
            {'name': 'VerdeFuerte', 'points': 220},
            {'name': 'EcoNinja', 'points': 190},
        ]
    }
    
    return render(request, 'hub.html', {
        'contexto_js': contexto_js  # Pasamos los datos al template
    })


# Vista para mostrar el formulario de verificación de imagen
class VerificarMobileNetView(View):
    def get(self, request):
        return render(request, 'verificar_mobilenet.html')

# Vista para manejar la subida y verificación de imagen
class SubirImagenView(View):
    
    def get(self, request):
        # Muestra el formulario de subida de imagen
        return render(request, 'verificar_mobilenet.html')

    def post(self, request):
        # 1. Obtiene la imagen del formulario
        archivo = request.FILES.get('imagen_subida')

        if not archivo:
            return HttpResponse("Error: No se envió ningún archivo.", status=400)

        # 2. Pasa la imagen al validador
        es_valida = es_imagen_relevante(archivo)

        # 3. Responde al usuario con el resultado de la predicción
        if es_valida:
            resultado = "¡IMAGEN ACEPTADA! ✅ Es una planta o basurero."
        else:
            resultado = "!Imagen rechazada"
        
        # Se pasa el resultado al template para mostrarlo
        return render(request, 'verificar_mobilenet.html', {'resultado': resultado})




#cosa nueva
