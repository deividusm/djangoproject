from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required(login_url='account_login')
def hub(request):
    return render(request, 'hub.html')   # hub.html está en templates/

