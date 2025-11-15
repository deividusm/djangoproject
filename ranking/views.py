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

# ==================================================================
# IMPORTS (Importaciones)
# ==================================================================

# --- Imports de Django ---
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.db.models import F  # <-- Importante para sumar puntos

# --- Imports de Autenticación ---
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

# --- Imports de tu App ---
from .models import Task, Profile  # Modelos para Tareas y Puntos
from mysite.image_validator import es_imagen_relevante # Tu validador de IA


# ==================================================================
# VISTAS DE AUTENTICACIÓN Y REGISTRO (Tu código)
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
# VISTAS DE TAREAS (CRUD) Y PUNTOS (Tu código)
# ==================================================================

class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'
    template_name = 'ranking/task_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['count'] = context['tasks'].filter(complete=False).count()

        # Obtiene o crea el perfil para mostrar los puntos
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
        # Esta lógica suma puntos si marcas la casilla "complete" manualmente
        old_task = Task.objects.get(pk=self.object.pk)
        was_completed = old_task.complete
        
        response = super().form_valid(form)
        
        new_task = self.object
        is_now_complete = new_task.complete
        
        profile, created = Profile.objects.get_or_create(user=self.request.user)

        if not was_completed and is_now_complete:
            profile.total_points = F('total_points') + new_task.points
            profile.save()
        elif was_completed and not is_now_complete:
            profile.total_points = F('total_points') - old_task.points
            profile.save()
            
        return response


class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')
    template_name = 'ranking/task_confirm_delete.html'


# ==================================================================
# VISTAS DE PÁGINAS ESTÁTICAS (Tu código)
# ==================================================================

@login_required(login_url='account_login')
def hub(request):
    return render(request, 'hub.html', {
        'usuario': request.user 
    })

@login_required(login_url='account_login')
def ranking(request):
    # ¡VISTA DE RANKING MEJORADA!
    # Ordena todos los perfiles por puntos (de mayor a menor) y toma el Top 10
    top_ranking = Profile.objects.order_by('-total_points')[:10]
    
    return render(request, 'ranking.html', {
        'ranking_list': top_ranking
    }) 

@login_required(login_url='account_login')
def comojugar(request):
    return render(request, 'comojugar.html')


# ==================================================================
# ¡VISTA CORREGIDA Y UNIFICADA! (Validación con IA y SQLite)
# ==================================================================

class SubirValidacionTaskView(LoginRequiredMixin, View):
    """
    Esta vista maneja la subida de una imagen para una TAREA específica.
    Usa el validador de IA (es_imagen_relevante) y suma puntos en SQLite.
    """
    template_name = 'ranking/validar_tarea.html'
    login_url = 'account_login' # O la URL de tu login

    def get(self, request, pk):
        """ Muestra el formulario de subida, específico para una tarea. """
        task = get_object_or_404(Task, pk=pk, user=request.user)
        
        return render(request, self.template_name, {
            'task': task,
            'resultado': None # Aún no hay resultado
        })

    def post(self, request, pk):
        """ 
        Recibe la imagen, la valida con la IA y suma los puntos.
        ¡ESTA ES LA LÓGICA 100% SQLITE!
        """
        
        # 1. Obtener la Tarea
        task = get_object_or_404(Task, pk=pk, user=request.user)

        # Si ya estaba completa, no hacer nada
        if task.complete:
            resultado = "Esta tarea ya fue completada."
            return render(request, self.template_name, {'task': task, 'resultado': resultado})

        # 2. Obtener el archivo
        archivo = request.FILES.get('imagen_subida')
        if not archivo:
            resultado = "Error: No se subió ningún archivo."
            return render(request, self.template_name, {'task': task, 'resultado': resultado})

        # 3. Llamar al validador de IA
        # (Tu image_validator.py devuelve True o False)
        print("Enviando imagen al validador de IA...")
        es_valida = es_imagen_relevante(archivo)
        print(f"Resultado de la IA: {es_valida}")

        # 4. Lógica de Puntos
        if es_valida:
            # ¡ÉXITO!
            
            # 4a. Marcar la tarea como completa
            task.complete = True
            task.save()
            
            # 4b. Sumar los puntos al Perfil del usuario
            # (Usamos get_or_create por si el perfil aún no existe)
            profile, created = Profile.objects.get_or_create(user=request.user)
            
            # Usamos F() para evitar 'race conditions' (buena práctica)
            # Le dice a la BD: "toma el valor actual y súmale task.points"
            profile.total_points = F('total_points') + task.points
            profile.save()
            
            resultado = f"¡IMAGEN ACEPTADA! ✅ Ganaste {task.points} puntos."
            
        else:
            # ¡FALLO!
            resultado = "¡Imagen rechazada! ❌ No se reconoció un objeto válido en la foto."

        # 5. Mostrar la página de nuevo con el resultado
        return render(request, self.template_name, {
            'task': task, 
            'resultado': resultado
        })
