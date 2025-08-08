from django.shortcuts import render, redirect, get_object_or_404
from .models import Clans, ClanStats,ClanJoinRequest
from django.utils.safestring import mark_safe
import markdown
from users.views import follow_toggle_view
from tournaments.models import ClanTournament
from django.contrib.auth.models import User
from users.models import Profile
from scripts.follow import *
from scripts import verify
from django.contrib.auth.decorators import login_required
from .forms import ClanRegistrationForm,AddPlayerToClanForm
from django.http import JsonResponse
from django.db.models import Q
from aries.settings import ErrorHandler
from django.contrib import messages
from django.db import transaction
from threading import Thread
@login_required
def clans(request):
    """
    Displays a list of clans, sorted by their Elo rating. Supports searching by clan name, ranking, country, or primary game.
    """
    query = request.GET.get('q', '')
    clans = Clans.objects.none()  
    no_results = True

    try:
        clans = Clans.objects.filter(is_verified=True)
        #to avoid users cuasing any potential follow issues
        if request.session.get('is_clan'):
            clan_id = request.session.get('clan_id')
            if clan_id:
                clans = clans.exclude(id=clan_id)
        if query:
            clans = clans.filter(
                Q(clan_name__icontains=query) |
                Q(stat__ranking__icontains=query) |
                Q(country__icontains=query) |
                Q(primary_game__icontains=query)
            ).distinct()
        
        no_results = not clans.exists()

    except Exception as e:
        ErrorHandler().handle(e, context='Clans loading view')

    return render(request, 'clans/clans.html', {
        'query': query,
        'clans': clans,
        'no_results': no_results
    })


@login_required
def request_to_join_clan(request, clan_id):
    """Allows a player to request to join a clan."""
    try:
        clan = get_object_or_404(Clans, id=clan_id)

        if ClanJoinRequest.objects.filter(player=request.user, clan=clan, status="pending").exists():
            return JsonResponse({"message": "You have already requested to join this clan. Contact admin if possible"}, status=400)

        ClanJoinRequest.objects.create(player=request.user, clan=clan)
        return JsonResponse({"message": "Request sent"}, status=200)

    except Exception as e:
        ErrorHandler().handle(e, context='Joining clan request')
        return JsonResponse({"message": "An error occurred while processing your request."}, status=500)

@login_required
def leave_clan(request,clan_id):
    """Allow players to leave clans"""
    try:
        profile = User.objects.get(username=request.user.username).profile
        profile.clan = None
        profile.save()
        messages.success(request, 'You have successfully left the clan.')
    except Exception as e:
        ErrorHandler().handle(e, context='Leaving Clan')
        messages.error(request, 'An error occurred while trying to leave the clan.')
    return redirect("clan_home")

def change_recruitment_state(request,clan_id):
    try:
        clan = get_object_or_404(Clans, id=clan_id)
        clan.is_recruiting = not clan.is_recruiting
        clan.save()
        messages.success(request,'Recruitment stage changed')
    except Exception as e:
        ErrorHandler().handle(e,context='Failed to change state')
        messages.error(request,'An error occurred while trying to change state')
    return redirect('clan_dashboard')
    
def change_description(request, clan_id):
    try:
        clan = get_object_or_404(Clans, id=clan_id)

        if request.method == "POST":
            new_description = request.POST.get("clan_description", "").strip()

            if not new_description:
                return JsonResponse({"error": "Description cannot be empty."}, status=400)

            clan.clan_description = new_description
            clan.save()
            return JsonResponse({"message": "Description updated successfully!"}) 
        
        return JsonResponse({"error": "Invalid request method."}, status=405)

    except Exception as e:
        ErrorHandler().handle(e, context='Description Changed')
        return JsonResponse({"error": "An unexpected error occurred."}, status=500)

def clan_view(request, clan_id):
    """
    Displays detailed information using the clan_id about a specific clan, including its stats, members, and recent match results.
    """
    try:
        clan = get_object_or_404(Clans, id=clan_id)
        clan_stats = get_object_or_404(ClanStats, id=clan_id)
        match_data = clan_stats.load_match_data_from_file()
        clan.clan_description = mark_safe(markdown.markdown(clan.clan_description))
        followers = count_followers(clan)
        following = count_following(clan)
        is_following = is_follower(get_logged_in_entity(request),clan)

        tournaments = ClanTournament.objects.filter(teams=clan).order_by('-id')[:5]

        match_results = []
        if match_data and "matches" in match_data:
            last_5_matches = match_data["matches"][-5:]
            match_results = [
                "W" if m["result"] == "win" else "L" if m["result"] == "loss" else "D"
                for m in last_5_matches
            ]
            match_data["matches"] = last_5_matches

        query = request.GET.get('q', '')
        if query:
            q_lower = query.lower()
            match_data["matches"] = [
                m for m in match_data["matches"]
                if any(q_lower in str(m[f]).lower() for f in ['date', 'tour_name', 'opponent', 'result', 'score'])
            ]

        members = User.objects.filter(profile__clan=clan)

        context = {
            'clan': clan,
            'stats': clan_stats,
            'players': members,
            'tournaments': tournaments,
            "match_results": match_results,
            "match_data": match_data,
            'query': query,
            'followers': followers,
            'following': following,
            'is_following': is_following
        }

        return render(request, 'clans/clan_view.html', context)

    except Exception as e:
        ErrorHandler().handle(e, context='clan_view')
        return render(request, 'clans/clan_view.html', {
            'error': "Something went wrong while loading the clan view."
        })

@login_required#ensures only users with accounts can create clubs needed for .created_by
def clan_register(request):
    """
    Handles clan registration. Validates the form and creates a new clan if the form is valid.
    """
    if request.method == 'POST':
        form = ClanRegistrationForm(request.POST,request.FILES)  
        if form.is_valid():
            try:
                with transaction.atomic():
                    clan = form.save(commit=False)
                    clan.created_by = request.user
                    request.user.profile.clan = clan
                    clan.set_password(form.cleaned_data['password'])
                    clan.save()
                    profile = request.user.profile
                    profile.clan = clan
                    profile.save()
                    Thread(target=verify.send_verification, args=(clan,)).start()

                    messages.info(request, "We've sent you a verification email.")
                    return redirect('verification_pending')
            except Exception as e:
                ErrorHandler().handle(e, context='clan_register')
                form.add_error(None, "Something went wrong during registration.")  
    else:
        form = ClanRegistrationForm()  
    return render(request, 'clans/create_clan.html', {'form': form})

def clan_login_required(view_func):
    """
    Custom decorator to ensure that only logged-in clans can access certain views.
    """
    def wrapper(request, *args, **kwargs):
        if 'clan_id' not in request.session:  
            return redirect('login')  
        return view_func(request, *args, **kwargs)
    return wrapper

@clan_login_required
def clan_dashboard(request):
    """
    Displays the dashboard for logged-in clans.
    """
    try:
        clan_id = request.session.get('clan_id')
        if not clan_id:
            messages.error(request, "Clan session missing.")
            return redirect("login")
        clan = get_object_or_404(Clans, id=clan_id)
        
        clan_stats = get_object_or_404(ClanStats, id=clan_id)
        try:
            match_data = clan_stats.load_match_data_from_file()
        except Exception as e:
            ErrorHandler().handle(e, context="Loading match data")
            match_data = {"matches": []}
        clan.clan_description = mark_safe(markdown.markdown(clan.clan_description))
        form = AddPlayerToClanForm(request.POST or None, clan=clan)
        members =User.objects.filter(profile__clan=clan)
        tournaments = ClanTournament.objects.filter(teams=clan)
        join_requests = ClanJoinRequest.objects.filter(clan=clan, status="pending")
        followers = count_followers(clan)
        following = count_following(clan)
    # ============================ get last 5 matches ============================ #
    # Match results
        match_results = []
        if match_data.get("matches"):
            last_5 = match_data["matches"][-5:]
            match_results = [
                "W" if m["result"] == "win"
                else "L" if m["result"] == "loss"
                else "D"
                for m in last_5
            ]
            match_data["matches"] = last_5

        # Search functionality
        query = request.GET.get('q', '').strip().lower()
        if query and match_data.get("matches"):
            match_data["matches"] = [
                m for m in match_data["matches"]
                if any(query in str(m.get(field, '')).lower()
                       for field in ['date', 'tour_name', 'opponent', 'result', 'score'])
            ] 
        context = {
            "clan": clan,
            "stats": clan_stats,
            "players": members,
            "tournaments": tournaments,
            "match_results": match_results,
            "match_data": match_data,
            "join_requests": join_requests,
            "form": form,
            "query": query,
            "followers": followers,
            "following": following,
        }
        return render(request, "clans/clan_dashboard.html", context)

    except Exception as e:
        ErrorHandler().handle(e, context="Clan dashboard view failure")
        messages.error(request, "Something went wrong while loading your dashboard.")
        return redirect("login")

def approve_reject(request):
    """
    Approves or rejects a pending clan join request.
    Only clan admins should have access to this.
    """
    try:
        request_id = request.POST.get("request_id")
        action = request.POST.get("manage_request")

        if not request_id or action not in ["approve", "reject"]:
            return JsonResponse({"error": "Missing or invalid request parameters."}, status=400)

        join_request = get_object_or_404(ClanJoinRequest, id=request_id)
        
        clan = join_request.clan

        if action == "approve":
            join_request.approve()
            msg = f"{join_request.player.username}'s join request approved."
        else:  
            join_request.reject()
            msg = f"{join_request.player.username}'s join request rejected."
        return JsonResponse({"message": msg})

    except Exception as e:
        ErrorHandler().handle(e, context="Clan join approval/rejection")
        return JsonResponse({"error": "An internal error occurred."}, status=500)

def add_remove_players(request):
    try:
        clan = get_object_or_404(Clans, id=request.session['clan_id'])
        if request.user != clan.created_by:
            return JsonResponse({"error": "You are not authorized to modify this clan."}, status=403)

        form = AddPlayerToClanForm(request.POST or None, clan=clan)
        if request.method == "POST" and form.is_valid():
            action = request.POST.get("action")
            player = form.cleaned_data.get("username")
            profile = get_object_or_404(Profile, user=player)

            if action == "add_player":
                if profile.clan:
                    return JsonResponse({"message": f"{player.username} is already in a clan!"})
                profile.clan = clan
                profile.save()
                return JsonResponse({"message": f"{player.username} has joined"})

            elif action == "remove_player":
                profile.clan = None
                profile.save()
                return JsonResponse({"message": f"{player.username} has been removed from the clan."})

        return JsonResponse({"error": "Invalid request"}, status=400)

    except Exception as e:
        ErrorHandler().handle(e, context='Add/Remove Player in Clan')
        return JsonResponse({"error": "Something went wrong while managing the clan members."}, status=500)


 

