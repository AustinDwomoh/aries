
from django.shortcuts import render, redirect,get_object_or_404
from .forms import ClanMatchScoreForm, IndiMatchScoreForm, ClanTournamentForm, IndiTournamentForm
from .models import ClanTournament, IndiTournament,Clans
def tours(request):
    cvc_tournaments = ClanTournament.objects.all()
    indi_tournaments = IndiTournament.objects.all()
    
    # Fetch matches for the CVC tournaments
    #cvc_matches = ClanMatch.objects.filter(tournament__in=cvc_tournaments)
    context = {"cvc_tournaments": cvc_tournaments,
               "indi_tournaments":indi_tournaments,
                }
    return render(request,'tournaments/tours.html',context)

def tours_cvc_view(request,tour_id):
    cvc_tournaments = get_object_or_404(ClanTournament, id=tour_id)
    match_data = cvc_tournaments.load_match_data_from_file()
    if cvc_tournaments.tour_type == "cup":
        for round in match_data["matches"]["rounds"]:
            for match in round["matches"]:
                team_a_user = get_object_or_404(Clans, clan_name=match["team_a"])
                team_b_user = get_object_or_404(Clans, clan_name=match["team_b"])
                # Assign profiles to match data
                match["team_a_logo"] = team_a_user.clan_logo
                match["team_b_logo"] = team_b_user.clan_logo
    elif cvc_tournaments.tour_type == "league":
        for round_key, round in match_data["matches"]["fixtures"].items():
            for match in round:
                team_a_profile = get_object_or_404(Clans, clan_name=match["team_a"])
                match["team_a_logo"] = team_a_profile.clan_logo 
                if match["team_b"] != "Bye":
                    team_b_profile = get_object_or_404(Clans, clan_name=match["team_b"])
                    match["team_b_logo"] = team_b_profile.clan_logo 
                else:
                    match["team_b_logo"] = None
        for team_name, team_stats in match_data["matches"]["table"].items():
            # Get the corresponding team profile from the Clans model
            team_profile = get_object_or_404(Clans, clan_name=team_name)
            # Add the team logo to the stats
            team_stats["team_logo"] = team_profile.clan_logo
                
 
    return render(request,'tournaments/cvc_tours_veiw.html',{'cvc_tour':cvc_tournaments, 'match_data': match_data  })

def tours_indi_view(request,tour_id):
    tournament = get_object_or_404(IndiTournament, id=tour_id)

    # Fetch matches related to the tournament
    """ matches = IndiMatch.objects.filter(tournament=tournament).select_related(
        'player_1', 'player_2', 'winner'
    )

    # Gather player statistics
    players = tournament.players.all()
    player_stats = []
    for player in players:
        matches_played = matches.filter(player_1=player) | matches.filter(player_2=player)
        total_wins = matches.filter(winner=player).count()
        total_draws = matches.filter(is_draw=True, player_1=player) | matches.filter(is_draw=True, player_2=player)
        total_losses = matches_played.count() - (total_wins + total_draws.count())
        
        player_stats.append({
            'player': player,
            'total_matches': matches_played.count(),
            'wins': total_wins,
            'draws': total_draws.count(),
            'losses': total_losses,
            'win_rate': round((total_wins / matches_played.count() * 100), 2) if matches_played.count() else 0,
        })

    context = {
        'tournament': tournament,
        'matches': matches,
        'players': player_stats,
        'recent_matches': matches.order_by('-match_date')[:5],  # Last 5 matches
    } """
    return render(request,'tournaments/indi_tours_veiw.html')
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