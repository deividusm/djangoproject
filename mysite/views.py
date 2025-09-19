from django.http import HttpResponse
import datetime
from django.template import Template, Context

def saludo(request):
    doc_externo = open(r"C:\Users\david\Desktop\djangoproject\mysite\plantillas\Untitled1.html")
    plt = Template(doc_externo.read())
    doc_externo.close()
    ctx =Context()
    documento =plt.render(ctx)
    return HttpResponse(documento)
