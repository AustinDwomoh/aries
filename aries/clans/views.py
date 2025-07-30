from django.shortcuts import render, redirect, get_object_or_404
from .models import Clans, ClanStats,ClanJoinRequest
from django.db.models import Q
from django.utils.safestring import mark_safe
import markdown
from tournaments.models import ClanTournament
from django.contrib.auth.models import User
from users.models import Profile
from django.contrib.auth.decorators import login_required
from .forms import ClanRegistrationForm, ClanLoginForm,AddPlayerToClanForm
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count,Q
from Home.models import Follow
from aries.settings import ErrorHandler
from django.contrib import messages
@login_required
def clans(request):
    """
    Displays a list of clans, sorted by their Elo rating. Supports searching by clan name, ranking, country, or primary game.
    """
    query = request.GET.get('q', '')
    clans = Clans.objects.none()  
    no_results = True

    try:
        clans = Clans.objects.select_related('stat').order_by('-stat__elo_rating')

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
    return redirect("clans_home")

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

        followed_type = ContentType.objects.get_for_model(Clans)
        follow_data = Follow.objects.filter(
            followed_type=followed_type, followed_id=clan_id
        ).aggregate(
            followers=Count('id'),
            following=Count('id', filter=Q(follower_id=clan_id))
        )

        followers = follow_data['followers']
        following = follow_data['following']
        is_following = Follow.objects.filter(
            followed_type=followed_type,
            followed_id=clan_id,
            follower_id=request.user.id
        ).exists()

        tournaments = ClanTournament.objects.filter(teams=clan).order_by('-id')[:5]

        # Match Result Parsing
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

        return render(request, 'clans/clan_veiw.html', context)

    except Exception as e:
        ErrorHandler().handle(e, context='clan_view')
        return render(request, 'clans/clan_view.html', {
            'error': "Something went wrong while loading the clan view."
        })

@login_required#ensures only users with accounts can create clubs
def clan_register(request):
    """
    Handles clan registration. Validates the form and creates a new clan if the form is valid.
    """
    if request.method == 'POST':
        form = ClanRegistrationForm(request.POST,request.FILES)  
        if form.is_valid():
            try:
                clan = form.save(commit=False)
                clan.created_by = request.user
                clan.set_password(form.cleaned_data['password'])
                clan.save()
                return redirect('clan_login')
            except Exception as e:
                ErrorHandler().handle(e, context='clan_register')
                form.add_error(None, "Something went wrong during registration.")  
    else:
        form = ClanRegistrationForm()  
    return render(request, 'clans/create_clan.html', {'form': form})

@login_required #ensures only users with accounts can create clubs
def clan_login(request):
    """
    Handles clan login. Validates the form and logs in the clan if the credentials are correct.
    """
    if request.method == 'POST':
        form = ClanLoginForm(request.POST)  
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                clan = Clans.objects.get(email=email)  
                request.session['clan_id'] = clan.id 
                return redirect('clan_dashboard')  
            except Clans.DoesNotExist:
                form.add_error('email', 'Clan not found.')
            except Exception as e:
                ErrorHandler().handle(e, context='clan_login')
                form.add_error(None, "Something went wrong during login.")  
    else:
        form = ClanLoginForm()  

    return render(request, 'clans/clan_login.html', {'form': form})

def clan_logout(request):
    """
    Handles clan logout by clearing the session data and redirecting to the login page.
    """
    request.session.flush()  # Clear all session data
    return redirect('clans/clan_login')  # Redirect to the login page

def clan_login_required(view_func):
    """
    Custom decorator to ensure that only logged-in clans can access certain views.
    """
    def wrapper(request, *args, **kwargs):
        if 'clan_id' not in request.session:  
            return redirect('clans/clan_login')  
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
            return redirect("some_fallback_view")
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
        followed_type = ContentType.objects.get_for_model(Clans)
        follow_data = Follow.objects.filter(
            followed_type=followed_type,
            followed_id=clan_id
        ).aggregate(
            followers=Count('id'),
            following=Count('id', filter=Q(follower_id=clan_id))
        )
   
        followers = follow_data.get('followers', 0)
        following = follow_data.get('following', 0)
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
        return redirect("clan_login")

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
        if not request.user.profile.clan == clan or  request.user != clan.created_by:
            return JsonResponse({"error": "You are not authorized to manage this request."}, status=403)

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

        # Authorization: Only clan creator can modify membership
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

def clan_follow_unfollow(request, action, followed_model, followed_id):
    """
    Allows a user or a club to follow or unfollow another user or club dynamically.
    :param action: "follow" or "unfollow"
    :param followed_id: ID of the entity being followed or unfollowed
    """
    try:
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return JsonResponse({"error": "You need to be logged in to follow or unfollow."}, status=401)
        # Determine follower type
        if isinstance(request.user, User):
            follower_type = ContentType.objects.get_for_model(User)
            follower_id = request.user.id
        else:
            follower_type = ContentType.objects.get_for_model(Clans)
            follower_id = request.clan.id 

    
        # Get the followed entity
        if followed_model != "clan":
            return JsonResponse({"error": "Invalid model type."}, status=400)

        followed_obj = get_object_or_404(Clans, id=followed_id)
        followed_type = ContentType.objects.get_for_model(followed_obj)
        if action == "follow":
            follow, created = Follow.objects.get_or_create(
                follower_type=follower_type,
                follower_id=follower_id,
                followed_type=followed_type,
                followed_id=followed_obj.id
            )
            msg = f"You are now following {followed_obj.clan_name}" if created else f"Already following {followed_obj.clan_name}"
            return JsonResponse({"context": {"message": msg}})
        
        elif action == "unfollow":
            deleted, _ = Follow.objects.filter(
                follower_type=follower_type,
                follower_id=follower_id,
                followed_type=followed_type,
                followed_id=followed_obj.id
            ).delete()
            msg = f"You have unfollowed {followed_obj.clan_name}" if deleted else "You weren't following this account"
            return JsonResponse({"context": {"message": msg}})
        return JsonResponse({"error": "Invalid action"}, status=400)
    except Exception as e:
        ErrorHandler().handle(e, context='Clan Follow/Unfollow')
        return JsonResponse({"error": "Unexpected error occurred."}, status=500)
 

