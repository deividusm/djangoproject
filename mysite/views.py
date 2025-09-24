from django.shortcuts import render

def aprende(request):
    return render(request, 'aprende.html')

def recicla(request):
    return render(request, 'recicla.html')




