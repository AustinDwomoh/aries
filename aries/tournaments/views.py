import time
from django.shortcuts import render, redirect,get_object_or_404,HttpResponse
from django.contrib.auth.decorators import login_required
import resend
from .forms import IndiTournamentForm, ClanTournamentForm,MatchResultForm
from .models import ClanTournament, IndiTournament, ClanTournamentPlayer
from django.conf import settings
from scripts.email_handle import notify_tournament_players
from clans.models import Clans
from users.models import Profile
from django.db.models import Count,Q
from django.contrib.auth.models import User
from django.urls import reverse
from .tourmanager import TourManager

def tours(request):
    """
    Display all tournaments (Clan vs Clan and Individual) with optional search.
    Results are ordered by number of participants (teams or players).
    """
    query = request.GET.get('q', '').strip()

    def filter_and_order(queryset, count_field, search_fields):
        """
        Annotates a queryset with a count field, orders by it (descending),
        and applies search filtering if a query is provided.
        """
        qs = queryset.annotate(count=Count(count_field)).order_by('-count')
        if query:
            search_filter = Q()
            for field in search_fields:
                search_filter |= Q(**{f"{field}__icontains": query})
            qs = qs.filter(search_filter)
        return qs

    cvc_tournaments = filter_and_order(ClanTournament.objects.all(),'teams',['name', 'tour_type'])
    indi_tournaments = filter_and_order(IndiTournament.objects.all(),'players',['name', 'tour_type']) 
    context = {
        "cvc_tournaments": cvc_tournaments,
        "indi_tournaments": indi_tournaments,
        "no_results_cvc": not cvc_tournaments.exists(),
        "no_results_indi": not indi_tournaments.exists(),
    }
    return render(request, 'tournaments/tours.html', context)

def tours_cvc_view(request,tour_id):
    """
    View for displaying a single Clan vs Clan tournament's match data.

    Args:
        request (HttpRequest): Incoming HTTP request object.
        tour_id (int): The primary key (ID) of the ClanTournament to display

    """
    cvc_tournaments = get_object_or_404(ClanTournament, id=tour_id)
    match_data = cvc_tournaments.load_match_data_from_file()
    tour_kind = 'cvc'

    match_data, rounds = process_tournament_data(cvc_tournaments.tour_type,match_data,resolver=resolve_team_clan,tournament=cvc_tournaments)
    return render(request, 'tournaments/tours_veiw.html', {
        'tour': cvc_tournaments,
        'match_data': match_data,
        'rounds': rounds,
        'tour_kind': tour_kind
    })

def tours_indi_view(request,tour_id):
    """
    View for displaying a single indi vs indi tournament's match data.

    Args:
        request (HttpRequest): Incoming HTTP request object.
        tour_id (int): The primary key (ID) of the Inditournament to display

    """
    indi_tournaments = get_object_or_404(IndiTournament, id=tour_id)
    match_data = indi_tournaments.load_match_data_from_file()
    tour_kind = 'indi'

    match_data, rounds = process_tournament_data(
        indi_tournaments.tour_type,
        match_data,
        resolver=resolve_team_user,
        tournament=indi_tournaments
    )

    return render(request, 'tournaments/tours_veiw.html', {
        'tour': indi_tournaments,
        'match_data': match_data,
        'rounds': rounds,
        'tour_kind': tour_kind
    })


@login_required
def create_clan_tournament(request):
    """
    Create a new Clan vs Clan (CVC) tournament.

    Behavior:
        - Requires the user to be logged in.
        - On GET: renders an empty form.
        - On POST: validates the form, assigns `created_by` as the current user,
          saves the tournament, and links selected teams.
        - Redirects to the CVC tournament details page after creation.

    Args:
        request (HttpRequest): HTTP request object.

    Returns:
        HttpResponse: Rendered template or redirect.
    """
    if request.method == 'POST':
        form = ClanTournamentForm(request.POST,request.FILES)
        if form.is_valid():
            tour = form.save(commit=False)
            tour.created_by = request.user  
            tour.save()  # Save to generate ID before setting M2M
            teams = form.cleaned_data.get('teams')
            tour.teams.set(teams)
            tour.save()  
            tour.logo = form.cleaned_data.get('logo', tour.logo)
            tour.save()  # Save the match instance
            notify_tournament_players('clan',request, tour, action="created")
            return redirect(reverse("cvc_details", kwargs={"tour_id": tour.id}))  
    else:
        form = ClanTournamentForm()

    return render(request, 'tournaments/create_clan_tour.html', {'form': form})

@login_required
def create_indi_tournament(request):
    """
    Create a new Individual tournament.

    Behavior:
        - Requires the user to be logged in.
        - On GET: renders an empty form.
        - On POST: validates the form, assigns `created_by` as the current user,
          saves the tournament, and links selected players.
        - Redirects to the individual tournament details page after creation.

    Args:
        request (HttpRequest): HTTP request object.

    Returns:
        HttpResponse: Rendered template or redirect.
    """
    if request.method == 'POST':
        form = IndiTournamentForm(request.POST, request.FILES,current_profile=request.user.profile)  # Handle files for logo

        if form.is_valid():
            tour = form.save(commit=False)
            tour.created_by = request.user
            tour.save()  # Save to generate ID before setting M2M
            tour.logo = form.cleaned_data.get('logo', tour.logo)  
            tour.players.set(form.cleaned_data.get('players', []))  # Link players
            tour.save()  # Save just incase
            notify_tournament_players('indi',request, tour, action="created")
            return redirect(reverse("indi_details", kwargs={"tour_id": tour.id}))
    else:
        form = IndiTournamentForm(current_profile=request.user.profile)
        
    return render(request, 'tournaments/create_indi_tour.html', {'form': form})

@login_required
def update_indi_tour(request, tour_id):
    """
    Update an Individual Tournament match result.

    Behavior:
        - Retrieves the tournament by ID (404 if not found).
        - Reads `team_a`, `team_b`, and round number (regular or knockout) from query params.
        - On GET: displays a form for entering match scores.
        - On POST: validates and updates the tournament data via its `update_tour()` method.
        - Redirects to tournament details after successful update.

    Args:
        request (HttpRequest): HTTP request object.
        tour_id (int): ID of the Individual Tournament to update.

    Query Parameters:
        team_a (str): Name of team A.
        team_b (str): Name of team B.
        round (int): Round number for league/group stages.
        kround (int): Knockout round number (if applicable).
        leg (int): Optional leg number for multi-leg matches.

    Returns:
        HttpResponse: Rendered template or redirect.
    """
    indi_tournament = get_object_or_404(IndiTournament, id=tour_id)
    team_a_name = request.GET.get('team_a', '')
    team_b_name = request.GET.get('team_b', '')
   
    # Determine round number (kround takes priority if present)
    round_num = int(request.GET.get('kround') or request.GET.get('round') or 0)
    leg_number = int(request.GET.get('leg', '0'))
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
                    "leg_number": leg_number
                }
            ]
           
            indi_tournament.update_tour(
                round_num,
                match_results,
                KO=bool(request.GET.get('kround'))
            )
            return redirect(reverse("indi_details", kwargs={"tour_id": indi_tournament.id}))
    else:
        form = MatchResultForm()

    return render(request, "tournaments/update_indi_tour.html", {
        "form": form, 
        "team_a_name": team_a_name,
        "team_b_name": team_b_name,
        "round": round_num,  
        "leg": leg_number
    })

@login_required
def assign_user_to_tournament(request, tournament_id, clan_id):
    """
    Assign a user to a clan for a given Clan Tournament.

    Behavior:
        - Accepts only POST requests.
        - Retrieves the target user, tournament, and clan (404 if any are missing).
        - If the tournament has 'fixed' player mode, returns a message instead of assigning.
        - Otherwise, creates the assignment if it does not exist already.

    Args:
        request (HttpRequest): Incoming HTTP request object.
        tournament_id (int): ID of the ClanTournament.
        clan_id (int): ID of the Clans entry.

    POST Data:
        user_id (int): ID of the user to assign.

    Returns:
        HttpResponse or HttpResponseRedirect:
            - Redirects to a success page on assignment.
            - Returns an error message for fixed mode or bad data.
    """
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        user = User.objects.get(pk=user_id)
        tournament = ClanTournament.objects.get(pk=tournament_id)
        clan = Clans.objects.get(pk=clan_id)

        if tournament.player_mode == 'fixed':
            return HttpResponse("Player assignments are fixed for this tournament.")
        
        ClanTournamentPlayer.objects.get_or_create(user=user, clan=clan, tournament=tournament)
        return redirect('some-success-page')

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

    round_num = int(request.GET.get('kround') or request.GET.get('round') or 0)
    leg_number = int(request.GET.get('leg', '0'))
        
   
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
            #pretty dure its never used
            match_data = {
                "player_a": player_a.user.username,
                "player_b": player_b.user.username,
                "team_a_goals": score_a,#due to how the tourmanager works
                "team_b_goals": score_b,
            }
            match_results.append(match_data)
            team_a_total_goals += score_a
            team_b_total_goals += score_b

            if score_a > score_b:
                team_a_wins += 1
            elif score_a < score_b:
                team_b_wins += 1
            TourManager().finalize_match_result(team_a=player_a.user.username, team_b=player_b.user.username, goals_a=score_a, goals_b=score_b,match=match_data)

        final_match_results = [{
        "round": round_num,
        "team_a": team_a_name,
        "team_b": team_b_name,
        "team_a_goals": team_a_wins,
        "team_a_player_goals": team_a_total_goals,
        "team_b_goals": team_b_wins,
        "team_b_player_goals": team_b_total_goals,
        "leg_number":leg_number
        }]
     
        # Update the tournament with the final match result
        cvc_tournaments.update_tour(
            round_num,
            final_match_results,KO=bool(request.GET.get('kround'))
        )
        return redirect(reverse("cvc_details", kwargs={"tour_id": cvc_tournaments.id}))

    return render(request, "tournaments/update_clan_tour.html", {
        "team_a_name": team_a_name,
        "team_b_name": team_b_name,
        "team_a_players": team_a_players,
        "team_b_players": team_b_players,
        "round": round_num,
    })

# ============================= Non veiw function ============================ #
def resolve_team_clan(name):
    """
    Resolves a clan name into display metadata (name + logo).

    Args:
        name (str): Clan name string, or "Bye"/None if no opponent.

    Returns:
        dict: {
            "display_name": (str) Clan's display name or "TBD" if unknown,
            "logo": (ImageField or None) Clan's logo if found
        }
    """
    if name == "Bye" or name is None:
        return {"display_name": "TBD", "logo": None}
    clan = get_object_or_404(Clans, clan_name=name)
    return {"display_name": clan.clan_name, "logo": clan.clan_logo}

def resolve_team_user(name):
    """
    Resolves a username into display metadata (name + profile picture).

    Args:
        name (str): Username string, or "Bye"/None if no opponent.

    Returns:
        dict: {
            "display_name": (str) User's username or "TBD" if unknown,
            "logo": (ImageField or None) User's profile picture if found
        }
    """
    if name == "Bye" or name is None:
        return {"display_name": "TBD", "logo": None}
    user = User.objects.get(username=name)
    return {"display_name": user.username, "logo": user.profile.profile_picture}

def process_tournament_data(tour_type, match_data, resolver, tournament):
    """
    Enriches tournament match data with display names and logos, depending on tournament type.

    Args:
        tour_type (str): Tournament format type ('cup', 'league', 'groups_knockout').
        match_data (dict): Raw match/tournament data structure.
        resolver (callable): Function to resolve a team identifier into a display dict.
        tournament (Model): Tournament object, used for fallback logo.

    Returns:
        tuple:
            - dict: Processed match_data with added display metadata.
            - list: Rounds array for rendering (used in group/knockout stages).
    """
    rounds = []
    # --- CUP FORMAT ---
    if tour_type == "cup":
        for round_data in match_data["rounds"]:
            for match in round_data["matches"]:
                for side in ["team_a", "team_b"]:
                    if side in match:
                        team_name = (match[side].get("name") if isinstance(match[side], dict) else match[side])
                        team_info = resolver(team_name)
                        match[f"{side}_display_name"] = team_info["display_name"]
                        match[f"{side}_logo"] = team_info["logo"] or tournament.logo
                    # Handle legs if present
                    if "legs" in match:
                        for leg_match in match["legs"]:
                            for side in ["team_a", "team_b"]:
                                if side in leg_match:
                                    team_name = ( leg_match[side].get("name") if isinstance(leg_match[side], dict) else leg_match[side])
                                    team_info = resolver(team_name)
                                    leg_match[f"{side}_display_name"] = team_info["display_name"]
                                    leg_match[f"{side}_logo"] = team_info["logo"] or tournament.logo                           
    
     # --- LEAGUE FORMAT ---
    elif tour_type == "league":
        for round_key, matches in match_data["fixtures"].items():
            for match in matches:
                for side in ["team_a", "team_b"]:
                    team_name = match.get(side)
                    team_info = resolver(team_name)
                    match[f"{side}_display_name"] = team_info["display_name"]
                    match[f"{side}_logo"] = team_info["logo"] or tournament.logo
        # Process table
        for team_name, team_stats in match_data["table"].items():
            team_info = resolver(team_name)
            team_stats["team_logo"] = team_info["logo"] or tournament.logo

     # --- GROUPS + KNOCKOUT FORMAT ---
    elif tour_type == "groups_knockout":
        for group_key, group_data in match_data.get("group_stages", {}).items():
            for round_number, matches in group_data.get("fixtures", {}).items():
                # Insert or extend the appropriate round
                current_round = next((r for r in rounds if r["round_number"] == round_number), None)
                if current_round:
                    current_round["matches"].extend(matches)
                else:
                    rounds.append({
                        "round_number": round_number,
                        "matches": matches[:],  
                    })
            # Enrich matches with team display names and logos
                for match in matches:
                    for side in ["team_a", "team_b"]:
                        team_name = match.get(side)
                        team_info = resolver(team_name)
                        match[f"{side}_display_name"] = team_info.get("display_name", team_name)
                        match[f"{side}_logo"] = team_info.get("logo") or tournament.logo

            # Enrich group table with team logos
            for team_name, stats in group_data.get("table", {}).items():
                team_info = resolver(team_name)
                stats["team_logo"] = team_info.get("logo") or tournament.logo

        # Handle knockout stage if it exists
        knockouts = match_data.get("knock_outs", {})
        if knockouts:
            for kround in knockouts.get("rounds", []):
                for match in kround.get("matches", []):
                    for side in ["team_a", "team_b"]:
                        team_name = match.get(side).get('name')
                        team_info = resolver(team_name)
                        match[f"{side}_display_name"] = team_info.get("display_name", team_name)
                        match[f"{side}_logo"] = team_info.get("logo") or tournament.logo

            for team_name, stats in knockouts.get("table", {}).items():
                team_info = resolver(team_name)
                stats["team_logo"] = team_info.get("logo") or tournament.logo
    return match_data, rounds
