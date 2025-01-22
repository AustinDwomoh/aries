from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import IndiTournamentForm, ClanTournamentForm,MatchResultForm
from .models import ClanTournament, IndiTournament,Clans
from users.models import Profile
from django.db.models import Count
from django.contrib.auth.models import User

def tours(request):
    cvc_tournaments = ClanTournament.objects.annotate(
        team_count=Count('teams')
    ).order_by('-team_count')

    indi_tournaments = IndiTournament.objects.annotate(
        player_count=Count('players')
    ).order_by('-player_count')

    context = {"cvc_tournaments": cvc_tournaments,
               "indi_tournaments":indi_tournaments,
                }
    return render(request,'tournaments/tours.html',context)

def tours_cvc_view(request,tour_id):
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
        
        for group_key, data in match_data['matches'].items():
            for round_number, matches in data["fixtures"].items():
                # Find the current round
                current_round = next(
                    (r for r in rounds if r["round_number"] == round_number), None
                )
                if current_round:
                    # Append matches to the existing round
                    current_round["matches"].extend(matches)
                else:
                    # Create a new round if it doesn't exist
                    rounds.append({
                        "round_number": round_number,
                        "matches": matches[:],  # Copy the matches list
                    })

                # Update match details with team logos
                for match in matches:
                    team_a_profile = get_object_or_404(Clans, clan_name=match["team_a"])
                    match["team_a_logo"] = team_a_profile.clan_logo
                    if match["team_b"] != "Bye":
                        team_b_profile = get_object_or_404(Clans, clan_name=match["team_b"])
                        match["team_b_logo"] = team_b_profile.clan_logo
                    else:
                        match["team_b_logo"] = None

    
        for group_name, group_data in match_data['matches'].items():
            for team_name, team_stats in group_data['table'].items():
                team_profile = get_object_or_404(Clans, clan_name=team_name)
                team_stats["team_logo"] = team_profile.clan_logo
    
    return render(request,'tournaments/cvc_tours_veiw.html',{'tour':cvc_tournaments, 'match_data': match_data,'rounds':rounds,'tour_kind':tour_kind  })

def tours_indi_view(request,tour_id):
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
        for group_key, data in match_data["matches"]['matches'].items():
            for round_number, matches in data["fixtures"].items():
                current_round = next((r for r in rounds if r["round_number"] == round_number), None)
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
        

        for group_name, group_data in match_data["matches"]['matches'].items():
            for team_name, team_stats in group_data['table'].items():
                team_profile =  User.objects.get(username=team_name)
                team_stats["team_logo"] = team_profile.profile.profile_picture


    return render(request,'tournaments/indi_tours_veiw.html',{'tour':indi_tournaments, 'match_data': match_data,'rounds':rounds,'tour_kind':tour_kind    })

""" from django.db.models import F, FloatField, Value
from django.db.models.functions import Rank

def get_player_leaderboard():
    return PlayerStats.objects.annotate(
        rank=Rank(
            expression=F('elo_rating'),
            output_field=FloatField()
        )
    ).order_by('-elo_rating')

def get_clan_leaderboard():
    return ClanStats.objects.annotate(
        rank=Rank(
            expression=F('elo_rating'),
            output_field=FloatField()
        )
    ).order_by('-elo_rating') """


@login_required
def create_clan_match(request):
    if request.method == 'POST':
        form = ClanTournamentForm(request.POST,request.FILES)
        if form.is_valid():
            match = form.save(commit=False)
            match.created_by = request.user  
            match.save()  
            teams = form.cleaned_data.get('teams')
            match.teams.set(teams)  
            match.save()
            match.logo = form.cleaned_data.get('logo', match.logo)
            match.save()  # Save the match instance
         
    else:
        form = ClanTournamentForm()

    return render(request, 'tournaments/create_clan_tour.html', {'form': form})

@login_required
def create_indi_tournament(request):
    if request.method == 'POST':
        form = IndiTournamentForm(request.POST, request.FILES)  # Handle files for logo
        if form.is_valid():
            match = form.save(commit=False)
            match.created_by = request.user  
            match.save()  
            players = form.cleaned_data.get('players')
            match.players.set(players)  
            match.save()
            match.logo = form.cleaned_data.get('logo', match.logo)
            match.save()
    else:
        form = IndiTournamentForm()

    return render(request, 'tournaments/create_indi_tour.html', {'form': form})



@login_required
def update_indi_tour(request, tour_id):
    indi_tournaments = get_object_or_404(IndiTournament, id=tour_id)
    team_a_name = request.GET.get('team_a', '')
    team_b_name = request.GET.get('team_b', '')
    
    round = request.GET.get('round', None)
    round_num = int(round)
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
            indi_tournaments.update_tour(round_num, match_results)
            return redirect('indi_details', tour_id=indi_tournaments.id)
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
    cvc_tournaments = get_object_or_404(ClanTournament, id=tour_id)
    team_names = [team.clan_name for team in cvc_tournaments.teams.all()]
    team_a_name = request.GET.get('team_a', '')
    team_b_name = request.GET.get('team_b', '')
    
    round = request.GET.get('round', None)
    round_num = int(round)
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
            cvc_tournaments.update_tour(round_num, match_results)
            return redirect('cvc_details', tour_id=cvc_tournaments.id)
    else:
        form = MatchResultForm()

    return render(request, "tournaments/update_clan_tour.html", {
        "form": form, 
        #"team_names": team_names, 
        "team_a_name": team_a_name,
        "team_b_name": team_b_name,
        'round':round
    })
