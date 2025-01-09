from django.shortcuts import render
from .models import Clans


def clubs(request):
    
    context = {
        'clans': Clans.objects.all().order_by('-date_joined')
    }
    
    return render(request, 'clubs/clubs.html', context)
