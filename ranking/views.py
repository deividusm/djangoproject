# ranking/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .image_validator import es_imagen_relevante
from .models import Profile, Task, ImagenesUsuario


# 🔹 Helper: lógica para validar imagen y otorgar puntos
def _otorgar_puntos_por_imagen(user, archivo, task=None):
    """
    Valida la imagen con MobileNet. 
    Si es válida:
      - suma puntos al Profile del usuario
      - guarda la imagen en ImagenesUsuario
      - marca la Task como completa (si existe)
    Devuelve: (es_valida, puntos_otorgados)
    """

    # 1) Validar la imagen con tu función de TensorFlow
    es_valida = es_imagen_relevante(archivo)

    puntos = 0

    if es_valida:
        # 2) Definir cuántos puntos dar
        if task is not None:
            puntos = task.points
        else:
            puntos = 10  # valor por defecto

        # 3) Asegurar que exista un Profile
        perfil, _ = Profile.objects.get_or_create(user=user)
        perfil.total_points += puntos
        perfil.save()

        # 4) Volver a poner el puntero del archivo al inicio para guardarlo
        try:
            archivo.seek(0)
        except Exception:
            pass

        # 5) Si no nos pasaron task, crear una genérica
        if task is None:
            task, _ = Task.objects.get_or_create(
                user=user,
                title="Acción de reciclaje registrada",
                defaults={
                    "description": "Acción genérica de reciclaje",
                    "points": puntos,
                },
            )

        # 6) Guardar la evidencia
        ImagenesUsuario.objects.create(
            user=user,
            task=task,
            imagen=archivo,
            puntos_otorgados=puntos,
        )

        # 7) Marcar la tarea como completa
        task.complete = True
        task.save()

    return es_valida, puntos


# 🔹 Hub
@login_required(login_url='account_login')
def hub(request):
    return render(request, 'hub.html', {
        'usuario': request.user,
    })


# 🔹 Ranking (vista que alimenta tu ranking.html)
@login_required(login_url='account_login')
def ranking(request):
    # Todos los perfiles ordenados por puntos
    jugadores = Profile.objects.select_related('user').order_by('-total_points')

    # Task genérica para el formulario de subir foto en ranking.html
    alguna_task, _ = Task.objects.get_or_create(
        user=request.user,
        title="Subir foto reciclaje",
        defaults={
            "description": "Sube una foto de tu acción de reciclaje para ganar puntos.",
            "points": 10,
        },
    )

    context = {
        'jugadores': jugadores,
        'alguna_task': alguna_task,
    }
    return render(request, 'ranking.html', context)


# 🔹 Cómo jugar
@login_required(login_url='account_login')
def comojugar(request):
    return render(request, 'comojugar.html')


# 🔹 Mapa de puntos
@login_required(login_url='account_login')
def mapapuntos(request):
    return render(request, 'mapapuntos.html')


# 🔹 Vista de "JUGAR" / subir acción con tu template verificar_mobilenet.html
class SubirImagenView(LoginRequiredMixin, View):
    login_url = 'account_login'

    def get(self, request):
        return render(request, 'verificar_mobilenet.html')

    def post(self, request):
        archivo = request.FILES.get('imagen_subida')

        if not archivo:
            return render(
                request,
                'verificar_mobilenet.html',
                {'resultado': "Error: no se envió ninguna imagen."},
                status=400
            )

        es_valida, puntos = _otorgar_puntos_por_imagen(request.user, archivo, task=None)

        if es_valida:
            resultado = f"¡IMAGEN ACEPTADA! ✅ Has ganado {puntos} puntos."
        else:
            resultado = "Imagen rechazada ❌. Sube una foto clara de planta/basurero."

        return render(request, 'verificar_mobilenet.html', {'resultado': resultado})


# 🔹 Vista para el formulario del RANKING
#     <form method="post" enctype="multipart/form-data"
#           action="{% url 'task-validate' alguna_task.id %}">
@login_required(login_url='account_login')
def task_validate(request, task_id):
    if request.method != 'POST':
        return HttpResponse("Método no permitido", status=405)

    # Aseguramos que la Task sea del usuario actual
    task = get_object_or_404(Task, id=task_id, user=request.user)

    archivo = request.FILES.get('imagen_subida')
    if not archivo:
        # Si quieres, más adelante puedes usar messages. Por ahora recargamos ranking.
        jugadores = Profile.objects.select_related('user').order_by('-total_points')
        return render(
            request,
            'ranking.html',
            {
                'jugadores': jugadores,
                'alguna_task': task,
                'error': "Debes seleccionar una imagen.",
            },
            status=400
        )

    es_valida, puntos = _otorgar_puntos_por_imagen(request.user, archivo, task=task)

    # Aquí podrías usar el framework de mensajes para decir "ganaste X puntos"
    # pero por simplicidad solo redirigimos al ranking.
    return redirect('ranking')

