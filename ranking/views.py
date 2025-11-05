from django.shortcuts import render
# --- Imports de Django ---
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.db import connection
# --- Imports de Autenticación ---
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

# --- Imports de tu App ---
from .models import Task, Profile
from mysite.image_validator import es_imagen_relevante # Importa la función de validación


# ==================================================================
# VISTAS DE AUTENTICACIÓN Y REGISTRO (Tu código 1)
# ==================================================================

class CustomLoginView(LoginView):
    template_name = 'ranking/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tasks')


class RegisterPage(FormView):
    template_name = 'ranking/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            # Crear un perfil para el nuevo usuario
            Profile.objects.create(user=user)
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)


# ==================================================================
# VISTAS DE TAREAS (CRUD) Y PUNTOS (Tu código 1)
# ==================================================================

class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'
    template_name = 'ranking/task_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['count'] = context['tasks'].filter(complete=False).count()

        profile, created = Profile.objects.get_or_create(user=self.request.user)
        context['total_points'] = profile.total_points

        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['tasks'] = context['tasks'].filter(
                title__icontains=search_input)

        context['search_input'] = search_input
        return context


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'ranking/task_detail.html'


class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description', 'complete', 'points']
    success_url = reverse_lazy('tasks')
    template_name = 'ranking/task_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)


class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'complete', 'points']
    success_url = reverse_lazy('tasks')
    template_name = 'ranking/task_form.html'

    def form_valid(self, form):
        old_task = Task.objects.get(pk=self.object.pk)
        was_completed = old_task.complete
        
        response = super().form_valid(form)
        
        new_task = self.object
        is_now_complete = new_task.complete
        
        profile, created = Profile.objects.get_or_create(user=self.request.user)

        if not was_completed and is_now_complete:
            profile.total_points += new_task.points
            profile.save()
        elif was_completed and not is_now_complete:
            profile.total_points -= old_task.points
            profile.save()
            
        return response


class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')
    template_name = 'ranking/task_confirm_delete.html'


# ==================================================================
# VISTAS DE PÁGINAS ESTÁTICAS (Tu código 2)
# ==================================================================

@login_required(login_url='account_login')
def hub(request):
    return render(request, 'hub.html', {
        'usuario': request.user 
    })

@login_required(login_url='account_login')
def ranking(request):
    # (Aquí podrías querer consultar todos los 'Profile' y ordenarlos por 'total_points')
    return render(request, 'ranking.html') 

@login_required(login_url='account_login')
def comojugar(request):
    return render(request, 'comojugar.html')


# ==================================================================
# ¡NUEVA VISTA CONECTADA! (Reemplaza SubirImagenView)
# ==================================================================

class SubirValidacionTaskView(LoginRequiredMixin, View):
    """
    Esta vista maneja la subida de una imagen para una TAREA específica.
    Espera la 'pk' (ID) de la tarea en la URL.
    """
    template_name = 'ranking/validar_tarea.html' # Un nuevo template
    login_url = 'account_login'

    def get(self, request, pk):
        """ Muestra el formulario de subida, específico para una tarea. """
        # Obtenemos la tarea que se quiere validar
        task = get_object_or_404(Task, pk=pk, user=request.user)
        
        # Si la tarea ya está completa, podemos mostrar un mensaje
        if task.complete:
            return render(request, self.template_name, {
                'task': task, 
                'resultado': 'Esta tarea ya fue completada.'
            })
            
        return render(request, self.template_name, {'task': task})
      # views.py (Solo la sección POST modificada)

# Asegúrate de importar tu nuevo modelo
# from .models import Task, Profile, ImagenSubida # <-- Agrega ImagenSubida



    
    def post(self, request, pk):
        
        # 1. Obtener la Tarea y el Perfil del usuario
        task = get_object_or_404(Task, pk=pk, user=request.user)
        # El perfil no es estrictamente necesario aquí si el trigger hace el trabajo,
        # pero lo mantendremos para referencia.
        
        archivo = request.FILES.get('imagen_subida')
        
        if not archivo or task.complete:
            # Manejo de errores simplificado...
            return redirect('tasks') # O renderizar un error
        try:
            profile = Profile.objects.get(user=request.user)
            # Asegúrate de que el UUID exista en el perfil
            user_uuid = profile.supabase_id 
            if user_uuid is None:
                 raise Exception("UUID no encontrado en el perfil.")
        except Profile.DoesNotExist:
            resultado = "Error: Perfil de usuario no configurado."
            return render(request, self.template_name, {'task': task, 'resultado': resultado})
        except Exception as e:
            resultado = f"Error al obtener UUID: {e}"
            return render(request, self.template_name, {'task': task, 'resultado': resultado})
        # 3. Llamar al validador de imagen
        # AHORA DEVUELVE EL ID DE LA CATEGORÍA (1 o 2) o None
        if not archivo or task.complete:
            return redirect('tasks') # Redirigir o manejar el error

        categoria_id_reconocida = es_imagen_relevante(archivo)
    
        # 4. ¡CONEXIÓN CON EL TRIGGER DE POSTGRESQL!
        if categoria_id_reconocida is not None:
            try:
                # 4a. Creamos una fila en la tabla 'imagenes_usuario'
                # ESTO ES LO QUE ACTIVA TU TRIGGER DE POSTGRESQL
                
                # Para la validación de la Tarea en Django (opcional):
                task.complete = True
                task.save()
                
                # Creamos la fila que activará el trigger.
                # Si usas el modelo con managed=False (PostgreSQL puro):
                with connection.cursor() as cursor:
                    # Usa la sentencia SQL nativa para asegurar que el trigger se dispara
                    cursor.execute("""
                        INSERT INTO public.imagenes_usuario ("user-id", categoria_id, url_imagen) 
                        VALUES (%s, %s, %s);
                    """, [user_uuid, categoria_id_reconocida, archivo.name]) 
                    # Nota: Guardar el archivo real requiere lógica de almacenamiento de Django.
                    # Aquí solo insertamos los IDs que necesita el trigger.
                
                # Si usas un modelo gestionado por Django:
                # ImagenSubida.objects.create(
                #     user=request.user, 
                #     categoria_id=categoria_id_reconocida,
                #     imagen=archivo 
                # )


                resultado = f"¡IMAGEN ACEPTADA! ✅ Categoría ID {categoria_id_reconocida} reconocida. El puntaje se sumó vía el Trigger de la BD."
            
            except Exception as e:
                 resultado = f"Error al guardar o activar el trigger: {e}"
                 
        else:
            resultado = "¡Imagen rechazada! ❌ No se reconoció 'potted_plant' o 'Trash_can'."

        # 5. Mostrar la página de nuevo con el resultado
        return render(request, self.template_name, {
            'task': task, 
            'resultado': resultado
        })

