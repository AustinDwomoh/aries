from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import IndiTournamentForm, ClanTournamentForm,MatchResultForm
from .models import ClanTournament, IndiTournament,Clans,ClanStats
from users.models import Profile
from django.db.models import Count,Q
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.urls import reverse
from . import images

def tours(request):
    """View function to display all tournaments with optional search functionality."""
    cvc_tournaments = ClanTournament.objects.annotate(
        team_count=Count('teams')
    ).order_by('-team_count')

    indi_tournaments = IndiTournament.objects.annotate(
        player_count=Count('players')
    ).order_by('-player_count')
    
    query = request.GET.get('q', '')
    if query:
        cvc_tournaments = cvc_tournaments.filter(
            Q(name__icontains=query) | 
            Q(tour_type__icontains=query) 
        )

        indi_tournaments = indi_tournaments.filter(
            Q(name__icontains=query) |
            Q(tour_type__icontains=query)
        )

    no_results_cvc = not cvc_tournaments.exists()
    no_results_indi = not indi_tournaments.exists()
 
    context = {
        "cvc_tournaments": cvc_tournaments,
        "indi_tournaments": indi_tournaments,
        "no_results_cvc": no_results_cvc,  
        "no_results_indi": no_results_indi,
    }
    return render(request, 'tournaments/tours.html', context)


def tours_cvc_view(request,tour_id):
    """View function to display details of a specific Clan vs Clan tournament."""
    cvc_tournaments = get_object_or_404(ClanTournament, id=tour_id)
    match_data = cvc_tournaments.load_match_data_from_file()
    tour_kind ='cvc'
    rounds = []
    
    if cvc_tournaments.tour_type == "cup":
        for round in match_data["rounds"]:
            for match in round["matches"]:
                team_a_user = get_object_or_404(Clans, clan_name=match["team_a"])
                team_b_user = get_object_or_404(Clans, clan_name=match["team_b"])
                # Assign profiles to match data
                match["team_a_logo"] = team_a_user.clan_logo
                match["team_b_logo"] = team_b_user.clan_logo
    elif cvc_tournaments.tour_type == "league":
        for round_key, round in match_data["fixtures"].items():
            for match in round:
                team_a_profile = get_object_or_404(Clans, clan_name=match["team_a"])
                match["team_a_logo"] = team_a_profile.clan_logo 
                if match["team_b"] != "Bye":
                    team_b_profile = get_object_or_404(Clans, clan_name=match["team_b"])
                    match["team_b_logo"] = team_b_profile.clan_logo 
                else:
                    match["team_b_logo"] = None
        for team_name, team_stats in match_data["table"].items():
            team_profile = get_object_or_404(Clans, clan_name=team_name)
            team_stats["team_logo"] = team_profile.clan_logo
    elif cvc_tournaments.tour_type == "groups_knockout":
        for group_key, data in match_data["group_stages"].items():
            for round_number, matches in data["fixtures"].items():
                # Find the current round
                current_round = next(
                    (r for r in rounds if r["round_number"] == round_number), None)
                if current_round:
                    current_round["matches"].extend(matches)
                else:
                    rounds.append({
                        "round_number": round_number,
                        "matches": matches[:],  
                    })
                for match in matches:
                    team_a_profile = get_object_or_404(Clans, clan_name=match["team_a"])
                    match["team_a_logo"] = team_a_profile.clan_logo
                    if match["team_b"] != "Bye":
                        team_b_profile = get_object_or_404(Clans, clan_name=match["team_b"])
                        match["team_b_logo"] = team_b_profile.clan_logo
                    else:
                        match["team_b_logo"] = None
            for team_name, team_stats in data['table'].items():
                team_profile = get_object_or_404(Clans, clan_name=team_name)
                team_stats["team_logo"] = team_profile.clan_logo
    
            
        if "knock_outs" in match_data and "rounds" in match_data["knock_outs"]:
            for kround in match_data["knock_outs"]["rounds"]:
                for match in kround["matches"]:
                    team_a_user = get_object_or_404(Clans, clan_name=match["team_a"])
                    team_b_user = get_object_or_404(Clans, clan_name=match["team_b"])
                    match["team_a_logo"] = team_a_user.clan_logo
                    match["team_b_logo"] = team_b_user.clan_logo
                for team_name, team_stats in match_data["knock_outs"]['table'].items():
                    team_profile = get_object_or_404(Clans, clan_name=team_name)
                    team_stats["team_logo"] = team_profile.clan_logo

    return render(request,'tournaments/cvc_tours_veiw.html',{'tour':cvc_tournaments, 'match_data': match_data,'rounds':rounds,'tour_kind':tour_kind  })


def tours_indi_view(request,tour_id):
    """View function to display details of a indi tournament."""
    indi_tournaments = get_object_or_404(IndiTournament, id=tour_id)
    match_data = indi_tournaments.load_match_data_from_file()
    tour_kind ='indi'
    rounds = []
    if indi_tournaments.tour_type == "cup":
        for round in match_data["rounds"]:    
            for match in round["matches"]: 
                team_a_user = User.objects.get(username=match['team_a'])
                team_b_user = User.objects.get(username=match['team_b'])
                # Assign profiles to match data
                match["team_a_logo"] = team_a_user.profile.profile_picture
                match["team_b_logo"] = team_b_user.profile.profile_picture
    elif indi_tournaments.tour_type == "league":
        for round_key, round in match_data["fixtures"].items():
            for match in round:
                team_a_user = User.objects.get(username=match['team_a'])
                match["team_a_logo"] = team_a_user.profile.profile_picture
                if match["team_b"] != "Bye":
                    team_b_user = User.objects.get(username=match['team_b'])
                    match["team_b_logo"] = team_b_user.profile.profile_picture
                else:
                    match["team_b_logo"] = None
        for team_name, team_stats in match_data["table"].items():
            team_user = User.objects.get(username=team_name)  # Fetch the User by username
            team_stats["team_logo"] = team_user.profile.profile_picture
    elif indi_tournaments.tour_type == "groups_knockout":
        for group_key, data in match_data["group_stages"].items():
            for round_number, matches in data["fixtures"].items():
                current_round = next(
                    (r for r in rounds if r["round_number"] == round_number), None)
                if current_round:
                    current_round["matches"].extend(matches)
                else:
                    rounds.append({
                        "round_number": round_number,
                        "matches": matches[:],  
                    })
                for match in matches:
                    if match["team_a"] != "Bye":
                        team_a_user = User.objects.get(username=match['team_a'])
                        match["team_a_logo"] = team_a_user.profile.profile_picture
                    else:
                        match["team_a_logo"] = None
                    if match["team_b"] != "Bye":
                        team_b_user = User.objects.get(username=match['team_b'])
                        match["team_b_logo"] = team_b_user.profile.profile_picture
                    else:
                        match["team_b_logo"] = None
            for team_name, team_stats in data['table'].items():
                team_profile =  User.objects.get(username=team_name)
                team_stats["team_logo"] = team_profile.profile.profile_picture

        if "knock_outs" in match_data and "rounds" in match_data["knock_outs"]:
            for kround in match_data["knock_outs"]["rounds"]:
                for match in kround["matches"]:
                    team_a_user = User.objects.get(username=match['team_a'])
                    team_b_user = User.objects.get(username=match['team_b'])
                    match["team_a_logo"] = team_a_user.profile.profile_picture
                    match["team_b_logo"] = team_b_user.profile.profile_picture
                for team_name, team_stats in match_data["knock_outs"]['table'].items():
                    team_profile = User.objects.get(username=team_name)
                    team_stats["team_logo"] = team_profile.profile.profile_picture

    return render(request,'tournaments/indi_tours_veiw.html',{'tour':indi_tournaments, 'match_data': match_data,'rounds':rounds,'tour_kind':tour_kind    })


@login_required
def create_clan_tournament(request):
    """View function to create a new Clan Tournament."""
    if request.method == 'POST':
        form = ClanTournamentForm(request.POST,request.FILES)
        if form.is_valid():
            tour = form.save(commit=False)
            tour.created_by = request.user  
            tour.save()  
            teams = form.cleaned_data.get('teams')
            tour.teams.set(teams)  
            tour.save()
            tour.logo = form.cleaned_data.get('logo', tour.logo)
            tour.save()  # Save the match instance
            return redirect(reverse("cvc_details", kwargs={"tour_id": tour.id}))  
    else:
        form = ClanTournamentForm()

    return render(request, 'tournaments/create_clan_tour.html', {'form': form})


@login_required
def create_indi_tournament(request):
    """View function to create a new indi Tournament."""
    if request.method == 'POST':
        form = IndiTournamentForm(request.POST, request.FILES)  # Handle files for logo
        if form.is_valid():
            tour = form.save(commit=False)
            tour.created_by = request.user  
            tour.save()  
            players = form.cleaned_data.get('players')
            tour.players.set(players)  
            tour.save()
            tour.logo = form.cleaned_data.get('logo', tour.logo)
            tour.save()
            return redirect(reverse("indi_details", kwargs={"tour_id": tour.id}))
    else:
        form = IndiTournamentForm()

    return render(request, 'tournaments/create_indi_tour.html', {'form': form})


@login_required
def update_indi_tour(request, tour_id):
    """View function to update an individual tournament match result."""
    indi_tournaments = get_object_or_404(IndiTournament, id=tour_id)
    team_a_name = request.GET.get('team_a', '')
    team_b_name = request.GET.get('team_b', '')
    
    round_num = int(request.GET.get('round', 0) or request.GET.get('kround', 0))
    if request.method == "POST":
        form = MatchResultForm(request.POST)
        if form.is_valid():
            match_results = [
                {
                    "round": round_num,
                    "team_a": team_a_name,
                    "team_b": team_b_name,
                    "team_a_goals": form.cleaned_data["team_a_goals"],
                    "team_b_goals": form.cleaned_data["team_b_goals"],
                }
            ]
            
            if request.GET.get('kround', None):
                indi_tournaments.update_tour(round_num, match_results, KO=True)
            else:
                indi_tournaments.update_tour(round_num, match_results)
            return redirect(reverse("indi_details", kwargs={"tour_id": indi_tournaments.id}))
    else:
        form = MatchResultForm()

    return render(request, "tournaments/update_indi_tour.html", {
        "form": form, 
        #"team_names": team_names, 
        "team_a_name": team_a_name,
        "team_b_name": team_b_name,
        'round':round
    })


@login_required
def update_clan_tour(request, tour_id):
    """View function to update a clan tournament match result."""
    cvc_tournaments = get_object_or_404(ClanTournament, id=tour_id)
    team_names = [team.clan_name for team in cvc_tournaments.teams.all()]

    team_a_name = request.GET.get('team_a', '')
    team_b_name = request.GET.get('team_b', '')

    team_a_clan = get_object_or_404(Clans, clan_name=team_a_name)
    team_b_clan = get_object_or_404(Clans, clan_name=team_b_name)

    team_a_players = list(team_a_clan.members.all())
    team_b_players = list(team_b_clan.members.all())

    round_num = int(request.GET.get('round', 0) or request.GET.get('kround', 0))
        
    def store_records(winner, loser, winner_goals, loser_goals, result_type="win"):
        """
        Update and store  records for the match result.

        Args:
            winner (Profile): The profile of the winning team.
            loser (Profile): The profile of the losing team.
            winner_goals (int): Goals scored by the winner.
            loser_goals (int): Goals scored by the loser.
            result_type (str): Type of result ('win', 'draw').
        """
        def get_player_stats(winner, loser):
            """Fetch PlayerStats instances for both winner and loser."""
            try:
                winner = User.objects.filter(username__iexact=winner).first()
                loser = User.objects.filter(username__iexact=loser).first()
                if winner and loser:
                    loser_stats = loser.profile.stats
                    winner_stats = winner.profile.stats 
                    return winner_stats, loser_stats
            except ObjectDoesNotExist:
                return None, None
            return None, None 

    
        winner_stats, loser_stats = get_player_stats(winner, loser)
        stats_used = "player_stats" 

        winner_data = winner_stats.load_match_data_from_file()
        loser_data = loser_stats.load_match_data_from_file()
        if result_type == "win":
            winner_result = "win"
            loser_result = "loss"
        elif result_type == "draw":
            winner_result = "draw"
            loser_result = "draw"
        winner_entry = {
            "date": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tour_name":f"{cvc_tournaments.name}-CvC", 
            "opponent": loser,  
            "result": winner_result, 
            "score": f"{winner_goals}:{loser_goals}"
        }
        loser_entry = {
            "date": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tour_name":f"{cvc_tournaments.name}-CvC",   
            "opponent": winner,  
            "result": loser_result, 
            "score":f"{loser_goals}:{winner_goals}"
        }

        if "matches" not in winner_data:
            winner_data["matches"] = []
        if "matches" not in loser_data:
            loser_data["matches"] = []

        winner_data["matches"].append(winner_entry)
        loser_data["matches"].append(loser_entry)
        winner_stats.match_data = winner_data 
        loser_stats.match_data = loser_data 
        winner_stats.save_match_data_to_file()
        loser_stats.save_match_data_to_file()

    def update_team_db_stats(team,gf,ga,result_type="draw"):
        """
        Update clan statistics based on the tournament results.
        """
        user = User.objects.get(username=team)
        user_stat = user.profile.stats
        user_stat.gd += gf-ga
        user_stat.gf += gf
        user_stat.ga += ga
        user_stat.games_played += 1
        if result_type =="win":
            user_stat.total_wins  += 1
        elif result_type == "loss":
            user_stat.total_losses += 1
        else:
            user_stat.total_draws  += 1
        win_rate = ((user_stat.total_wins + user_stat.total_draws/2) / user_stat.games_played) * 100 if user_stat.games_played > 0 else 0
        user_stat.win_rate = round(win_rate,3)
        user_stat.save()
    
    def update_elo_for_match(winner_name, loser_name, k=32):
        """
        Update Elo ratings for a match.

        Args:
            winner_name (str): Name of the winner (player or clan).
            loser_name (str): Name of the loser (player or clan).
            PlayerStatsModel: Django model for player stats.
            ClanStatsModel: Django model for clan stats.
            k (int): The K-factor for Elo calculation (default: 32).

        Returns:
            None: Updates the database directly.
        """
        def get_player_elo_and_instance(name):
            """Fetch Elo rating and instance from a given player model."""
            #player = User.objects.get(username=name)
            player = User.objects.filter(username__iexact=name).first()
            if player:
                instance = player.profile.stats
                return instance.elo_rating, instance
            else:
                return None, None
            
        def update_elo(winner_elo, loser_elo, k):
            """Calculate Elo rating adjustments."""
            expected_winner = 1 / (1 + 10 ** ((loser_elo - winner_elo) / 400))
            winner_new_elo = winner_elo + k * (1 - expected_winner)
            loser_new_elo = loser_elo - k * (1 - expected_winner)
            return winner_new_elo, loser_new_elo
        winner_elo, winner_instance = get_player_elo_and_instance(winner_name)
        loser_elo, loser_instance = get_player_elo_and_instance(loser_name)

        winner_new_elo, loser_new_elo = update_elo(winner_elo, loser_elo, k)
        if winner_instance:
            winner_instance.elo_rating = winner_new_elo
            winner_instance.save()
            winner_instance.set_rank_based_on_elo()

        if loser_instance:
            loser_instance.elo_rating = loser_new_elo
            loser_instance.save()
            loser_instance.set_rank_based_on_elo()
    

    if request.method == "POST":
        player_a_ids =  [request.POST[key] for key in request.POST if key.startswith('player_a_')]
        player_b_ids = [request.POST[key] for key in request.POST if key.startswith('player_b_')]
        scores_a = [request.POST[key] for key in request.POST if key.startswith('score_a_')]
        scores_b = [request.POST[key] for key in request.POST if key.startswith('score_b_')]
        match_results = []
        team_a_total_goals, team_b_total_goals = 0, 0
        team_a_wins, team_b_wins = 0, 0

        if len(player_a_ids) != len(player_b_ids):
            return redirect(request.path)

        for i in range(len(player_a_ids)):
            player_a = get_object_or_404(Profile, id=player_a_ids[i])
            player_b = get_object_or_404(Profile, id=player_b_ids[i])
            score_a, score_b = int(scores_a[i]), int(scores_b[i])

            match_results.append({
                "player_a": player_a.user.username,
                "player_b": player_b.user.username,
                "player_a_score": score_a,
                "player_b_score": score_b,
            })
            team_a_total_goals += score_a
            team_b_total_goals += score_b

            if score_a > score_b:
                team_a_wins += 1
                store_records(player_a.user.username, player_b.user.username, score_a, score_b)
                update_team_db_stats(player_a.user.username, score_a, score_b, "win")
                update_team_db_stats(player_b.user.username, score_b, score_a, "loss")
                update_elo_for_match(player_a.user.username, player_b.user.username)
            elif score_a < score_b:
                team_b_wins += 1
                store_records(player_b.user.username, player_a.user.username, score_b, score_a)
                update_team_db_stats(player_a.user.username, score_a, score_b, "loss")
                update_team_db_stats(player_b.user.username, score_b, score_a, "win")
                update_elo_for_match(player_b.user.username, player_a.user.username)
            else:
                store_records(player_a.user.username, player_b.user.username, score_a, score_b, "draw")
                update_team_db_stats(player_a.user.username, score_a, score_b, "draw")
                update_team_db_stats(player_b.user.username, score_b, score_a, "draw")

        final_match_results = [{
        "round": round_num,
        "team_a": team_a_name,
        "team_b": team_b_name,
        "team_a_goals": team_a_wins,
        "team_a_player_goals": team_a_total_goals,
        "team_b_goals": team_b_wins,
        "team_b_player_goals": team_b_total_goals,
        }]
        team_a_clan_stat = ClanStats.objects.get(clan__clan_name=team_a_name)
        team_b_clan_stat = ClanStats.objects.get(clan__clan_name=team_b_name)

        team_a_clan_stat.player_scored += team_a_total_goals
        team_b_clan_stat.player_scored += team_b_total_goals
        team_a_clan_stat.player_conceeded += team_b_total_goals
        team_b_clan_stat.player_conceeded += team_a_total_goals
        team_a_clan_stat.save()
        team_b_clan_stat.save()

        if request.GET.get('kround'):
            cvc_tournaments.update_tour(round_num, final_match_results, KO=True)
        else:
            cvc_tournaments.update_tour(round_num, final_match_results)

        return redirect(reverse("cvc_details", kwargs={"tour_id": cvc_tournaments.id}))

    return render(request, "tournaments/update_clan_tour.html", {
        "team_a_name": team_a_name,
        "team_b_name": team_b_name,
        "team_a_players": team_a_players,
        "team_b_players": team_b_players,
        "round": round_num,
    })

def get_image(request,tour_id):
    cvc_tournaments = get_object_or_404(ClanTournament, id=tour_id)
    match_data = cvc_tournaments.load_match_data_from_file()
    tour_kind ='cvc'
    images.generate_table_image(match_data)
    return redirect('cvc_details')
    


    