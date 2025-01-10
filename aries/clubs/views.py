from django.shortcuts import render
from .models import Clans
from django.contrib.auth.decorators import login_required

@login_required
def clubs(request):
    
    context = {
        'clans': Clans.objects.all().order_by('-date_joined')
    }
    
    return render(request, 'clubs/clubs.html', context)
