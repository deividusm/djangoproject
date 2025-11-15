# mysite/views.py
from django.shortcuts import redirect

def root_redirect(request):
    # Si algún día quieres usarlo, te manda al home de ranking
    return redirect('home')
