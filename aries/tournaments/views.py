
from django.shortcuts import render, redirect,get_object_or_404
from .forms import ClanMatchScoreForm, IndiMatchScoreForm, ClanTournamentForm, IndiTournamentForm
from .models import ClanMatch, IndiMatch,ClanTournament, IndiTournament
def tours(request):
    cvc_tournaments = ClanTournament.objects.all()
    indi_tournaments = IndiTournament.objects.all()
    
    # Fetch matches for the CVC tournaments
    cvc_matches = ClanMatch.objects.filter(tournament__in=cvc_tournaments)
    context = {"cvc_tournaments": cvc_tournaments,
               "indi_tournaments":indi_tournaments,
                "cvc_matches": cvc_matches,}
    return render(request,'tournaments/tours.html',context)

""" # For Clan Matches
def input_clan_scores(request, pk):
    match = get_object_or_404(ClanMatch, pk=pk)

    if request.method == "POST":
        form = ClanMatchScoreForm(request.POST, instance=match)
        if form.is_valid():
            # Save the updated match data
            form.save()

            # Call model methods to process updates
            match.calculate_player_match_result()

            # Redirect to a success page or the match detail
            return redirect('match_detail', pk=match.pk)
    else:
        form = ClanMatchScoreForm(instance=match)
    return render(request, 'tournaments/input_clan_scores.html', {'form': form, 'match': match})

# For Individual Matches
def input_indi_scores(request, match_id):
    match = IndiMatch.objects.get(id=match_id)

    if request.method == 'POST':
        form = IndiMatchScoreForm(request.POST, instance=match)
        if form.is_valid():
            form.save()  # This will update the match scores and automatically update stats
            return redirect('tournaments/match_results', match_id=match.id)
    else:
        form = IndiMatchScoreForm(instance=match)

    return render(request, 'tournaments/input_indi_scores.html', {'form': form, 'match': match})


def create_clan_tournament(request):
    if request.method == 'POST':
        form = ClanTournamentForm(request.POST)
        if form.is_valid():
            tournament = form.save(commit=False)
            tournament.created_by = request.user
            tournament.save()
            form.save_m2m()  # Save ManyToMany fields
            return redirect('list_clan_tournaments')
    else:
        form = ClanTournamentForm()

    return render(request, 'tournaments/create_clan_tournament.html', {'form': form})

def list_clan_tournaments(request):
    tournaments = ClanTournament.objects.all()
    return render(request, 'tournaments/list_clan_tournament.html', {'tournaments': tournaments})

# IndiTournament View
def create_indi_tournament(request):
    if request.method == 'POST':
        form = IndiTournamentForm(request.POST)
        if form.is_valid():
            tournament = form.save(commit=False)
            tournament.created_by = request.user
            tournament.save()
            form.save_m2m()  # Save ManyToMany fields
            return redirect('list_indi_tournaments')
    else:
        form = IndiTournamentForm()

    return render(request, 'tournaments/create_indi_tournament.html', {'form': form})

def list_indi_tournaments(request):
    tournaments = IndiTournament.objects.all()
    return render(request, 'tournaments/list_indi_tournament.html', {'tournaments': tournaments})"""