from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm
from .models import Clans
from django.contrib.auth.models import User


# Create your views here.
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,f"Your account has been created! You can login")
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form':form})

@login_required
def profile(request):
    return render(request, 'users/profile.html',)

def all_gamers(request):
    players = User.objects.all()
    return render(request,'users/gamers.html',{'players':players})

""" 
def clan_profile(request, clan_id):
    clan = Clans.objects.get(id=clan_id)
    last_5_wins = clan.last_5_wins()
    last_5_matches = clan.last_5_matches()
    return render(request, 'clan_profile.html', {
        'clan': clan,
        'last_5_wins': last_5_wins,
        'last_5_matches': last_5_matches,
    })

def last_5_wins(self):

    return Match.objects.filter(winner=self).order_by('-match_date')[:5]

def last_5_matches(self):
    matches = Match.objects.filter(team_1=self) | Match.objects.filter(team_2=self)
    return matches.order_by('-match_date')[:5] """

""" def player_matches(request):
    player = request.user  # Assuming you're using the logged-in user
    # Get the player's associated clan(s) (this might differ based on your actual model relationships)
    clans = player.clans.all()
    
    # Fetch the last 5 matches for the player's teams
    player_matches = Match.objects.filter(
        team_1__in=clans).or(Match.objects.filter(team_2__in=clans)).order_by('-match_date')[:5]

    return render(request, 'player_matches.html', {'player_matches': player_matches}) """

""" def player_profile(request):
    player = request.user  # Assuming logged-in user
    # Get the player's associated clan(s)
    clans = player.clans.all()
    
    # Fetch the last 5 matches
    last_matches = Match.objects.filter(
        team_1__in=clans
    ).or(Match.objects.filter(team_2__in=clans)).order_by('-match_date')[:5]

    # Create a list of results (W for Win, L for Loss, D for Draw)
    match_results = []
    for match in last_matches:
        if match.winner == match.team_1:
            match_results.append('W')  # Win
        elif match.winner == match.team_2:
            match_results.append('L')  # Loss
        else:
            match_results.append('D')  # Draw

    return render(request, 'player_profile.html', {'match_results': match_results}) """