from django.shortcuts import render
from .models import Clans
from django.contrib.auth.decorators import login_required

@login_required
def clubs(request):
    
    context = {
        'clans': Clans.objects.all().order_by('-date_joined')
    }
    
    return render(request, 'clubs/clubs.html', context)
""" def clan_detail(request, clan_id):
    clan = Clans.objects.get(id=clan_id)
    members = clan.members.all()  # All profiles linked to the clan
    return render(request, 'clan_detail.html', {'clan': clan, 'members': members}) """
