
from django.shortcuts import render, redirect,get_object_or_404
from .forms import ClanMatchScoreForm, IndiMatchScoreForm, ClanTournamentForm, IndiTournamentForm
from .models import ClanTournament, IndiTournament,Clans
from users.models import Profile
from django.contrib.auth.models import User
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
    elif cvc_tournaments.tour_type == "groups_knockout":
        rounds = []
        for group_key, data in match_data["matches"]['matches'].items():
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

    
        for group_name, group_data in match_data["matches"]['matches'].items():
            for team_name, team_stats in group_data['table'].items():
                team_profile = get_object_or_404(Clans, clan_name=team_name)
                team_stats["team_logo"] = team_profile.clan_logo
    
    return render(request,'tournaments/cvc_tours_veiw.html',{'cvc_tour':cvc_tournaments, 'match_data': match_data,'rounds':rounds  })

def tours_indi_view(request,tour_id):
    indi_tournaments = get_object_or_404(IndiTournament, id=tour_id)
    match_data = indi_tournaments.load_match_data_from_file()
    if indi_tournaments.tour_type == "cup":
        for round in match_data["matches"]["rounds"]:
            for match in round["matches"]:
                team_a_user = User.objects.get(username=match['team_a'])
                team_b_user = User.objects.get(username=match['team_b'])
                # Assign profiles to match data
                match["team_a_logo"] = team_a_user.profile.profile_picture
                match["team_b_logo"] = team_b_user.profile.profile_picture
    elif indi_tournaments.tour_type == "league":
        for round_key, round in match_data["matches"]["fixtures"].items():
            for match in round:
                team_a_user = User.objects.get(username=match['team_a'])
                match["team_a_logo"] = team_a_user.profile.profile_picture
                if match["team_b"] != "Bye":
                    team_b_user = User.objects.get(username=match['team_b'])
                    match["team_b_logo"] = team_b_user.profile.profile_picture
                else:
                    match["team_b_logo"] = None
        for team_name, team_stats in match_data["matches"]["table"].items():
            team_user = User.objects.get(username=team_name)  # Fetch the User by username
            team_stats["team_logo"] = team_user.profile.profile_picture
    elif indi_tournaments.tour_type == "groups_knockout":
        rounds = []
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


    return render(request,'tournaments/indi_tours_veiw.html',{'indi_tour':indi_tournaments, 'match_data': match_data,'rounds':rounds   })
