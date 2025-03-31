from django.shortcuts import render, redirect, get_object_or_404
from .models import Clans, ClanStats,ClanJoinRequest
from django.db.models import Q
from django.contrib.auth.models import User
from users.models import Profile
from django.contrib.sessions.models import Session
from django.contrib.auth.decorators import login_required
from .forms import ClanRegistrationForm, ClanLoginForm,AddPlayerToClanForm
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count,Q
from Home.models import Follow

@login_required
def clubs(request):
    """
    Displays a list of clans, sorted by their Elo rating. Supports searching by clan name, ranking, country, or primary game.
    """
    query = request.GET.get('q', '')  # Get the search query from the request
    clans = Clans.objects.all().select_related('stat').order_by('-stat__elo_rating')  # Fetch all clans with their stats, sorted by Elo rating

    if query:
        clans = clans.filter(
            Q(clan_name__icontains=query) |  
            Q(stat__ranking__icontains=query) | 
            Q(country__icontains=query) | 
            Q(primary_game__icontains=query)
        ).distinct()  
    no_results = not clans.exists()  # Check if no clans match the search query
    return render(request, 'clubs/clubs.html', {'query': query, 'clans': clans, 'no_results': no_results})

@login_required
def request_to_join_clan(request, clan_id):
    """Allows a player to request to join a clan."""
    clan = get_object_or_404(Clans, id=clan_id)

    existing_request = ClanJoinRequest.objects.filter(player=request.user, clan=clan, status="pending").exists()
    if existing_request:
        print('here')
        return JsonResponse({"message": "You have already requested to join this clan.Contact admin if possible"})
    ClanJoinRequest.objects.create(player=request.user, clan=clan)
    print('here1')
    return JsonResponse({"message": "Request sent"})

def leave_clan(request,clan_id):
    """Allow players to leave clans"""
    clan = get_object_or_404(Clans, id=clan_id)
    
    profile = User.objects.get(username=request.user.username).profile
    profile.clan = None
    profile.save()
    return redirect("clubs-home")

def change_recruitment_state(request,clan_id):
    clan = get_object_or_404(Clans, id=clan_id)
    clan.is_recruiting = not clan.is_recruiting
    clan.save()
    return redirect('clan_dashboard')
    
def club_view(request, clan_id):
    """
    Displays detailed information using the clan_id about a specific clan, including its stats, members, and recent match results.
    """
    clan = get_object_or_404(Clans, id=clan_id)  # Fetch the clan or return a 404 error if not found
    clan_stats = get_object_or_404(ClanStats, id=clan_id)  # Fetch the clan's stats
    match_data = clan_stats.load_match_data_from_file()  # Load match data from the JSON file
    # Process match results for display
    # Fetching followers and following count for the club
    # ============================================================================ #
    #                          Fetching followers and following count                #
    # ============================================================================ #
    followed_type = ContentType.objects.get_for_model(Clans)
    followed_type = ContentType.objects.get_for_model(Clans)
    follow_data = Follow.objects.filter(followed_type=followed_type, followed_id=clan_id).aggregate(followers=Count('id'),
following=Count('id', filter=Q(follower_id=clan_id))
    )
    followers = follow_data['followers']
    following = follow_data['following']
    is_following =  Follow.objects.filter(followed_type=followed_type, followed_id=clan_id, follower_id=request.user.id).exists()
  
   # ============================================================================ #
   #                          Check for clan matches data                         #
   # ============================================================================ #
    match_results = []
    if match_data:
        last_5_matches = match_data["matches"][-5:]  # Get last 5 matches
        match_results = ["W" if match["result"] == "win" else "L" if match["result"] == "loss" else "D" for match in last_5_matches]
        match_data["matches"] = last_5_matches  # Avoid slicing again later
    
    # ========================= searching for match data ========================= #
    query = request.GET.get('q', '')
    if query:
        # Filter players using list comprehension
        query_lower = query.lower()
        match_data["matches"] = [
            match for match in match_data['matches']
            if any(query_lower in str(match[field]).lower() for field in ['date', 'tour_name', 'opponent', 'result', 'score'])
        ]
    #no_results = not match_data["matches"]

    members =User.objects.filter(profile__clan=clan)
    context = {
        'clan': clan,
        'stats': clan_stats,
        'players': members,
        "match_results": match_results,
        "match_data": match_data,
        'query':query,
        'followers':followers,
        'following':following,
        'is_following': is_following# Check if the user is following the clan
    }
    return render(request, 'clubs/club_veiw.html', context)

@login_required#ensures only users with accounts can create clubs
def clan_register(request):
    """
    Handles clan registration. Validates the form and creates a new clan if the form is valid.
    """
    if request.method == 'POST':
        form = ClanRegistrationForm(request.POST,request.FILES)  
        created_by = request.user
        if form.is_valid():
            clan = form.save(commit=False)  # Create a clan instance but don't save it yet
            clan.created_by = request.user
            clan.set_password(form.cleaned_data['password'])  # Hash the password
            clan.save()  # Save the clan to the database
            return redirect('clan_login')  # Redirect to the login page after registration
    else:
        form = ClanRegistrationForm()  
    return render(request, 'clubs/create_club.html', {'form': form})

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
                clan = Clans.objects.get(email=email)  # Fetch the clan by email
                #if clan.check_password(password):  # Verify the password
                request.session['clan_id'] = clan.id  # Store the clan ID in the session
                return redirect('clan_dashboard')  # Redirect to the dashboard
                #else:
                    #form.add_error('password', 'Incorrect password.')  # Add an error for incorrect password
            except Clans.DoesNotExist:
                form.add_error('email', 'Clan not found.')  # Add an error if the clan doesn't exist
    else:
        form = ClanLoginForm()  # Display an empty form for GET requests

    return render(request, 'clubs/clan_login.html', {'form': form})

def clan_logout(request):
    """
    Handles clan logout by clearing the session data and redirecting to the login page.
    """
    request.session.flush()  # Clear all session data
    return redirect('clubs/clan_login')  # Redirect to the login page

def clan_login_required(view_func):
    """
    Custom decorator to ensure that only logged-in clans can access certain views.
    """
    def wrapper(request, *args, **kwargs):
        if 'clan_id' not in request.session:  # Check if the clan is logged in
            return redirect('clubs/clan_login')  # Redirect to the login page if not logged in
        return view_func(request, *args, **kwargs)
    return wrapper

@clan_login_required
def clan_dashboard(request):
    """
    Displays the dashboard for logged-in clans.
    """
    clan = get_object_or_404(Clans, id=request.session['clan_id'])
    clan_stats = get_object_or_404(ClanStats, id=request.session['clan_id'])
    match_data = clan_stats.load_match_data_from_file()
    form = AddPlayerToClanForm(request.POST or None, clan=clan)
    members =User.objects.filter(profile__clan=clan)
    join_requests = ClanJoinRequest.objects.filter(clan=clan, status="pending")
    followed_type = ContentType.objects.get_for_model(Clans)
    followed_type = ContentType.objects.get_for_model(Clans)
    follow_data = Follow.objects.filter(followed_type=followed_type, followed_id=request.session['clan_id']).aggregate(followers=Count('id'),
following=Count('id', filter=Q(follower_id=request.session['clan_id']))
    )
    followers = follow_data['followers']
    following = follow_data['following']
    # ============================ get last 5 matches ============================ #
    match_results = []
    if match_data:
        last_5_matches = match_data["matches"][-5:]  # Get last 5 matches
        match_results = ["W" if match["result"] == "win" else "L" if match["result"] == "loss" else "D" for match in last_5_matches]
        match_data["matches"] = last_5_matches

    # ============================ searching for match data ============================ #
   
    query = request.GET.get('q', '')
    if query:
        # Filter players using list comprehension
        query_lower = query.lower()
        match_data["matches"] = [
            match for match in match_data['matches']
            if any(query_lower in str(match[field]).lower() for field in ['date', 'tour_name', 'opponent', 'result', 'score'])
        ]
        
        
    context = {
        "clan": clan,
        "stats": clan_stats,
        "players": members,
        "match_results": match_results,
        "match_data": match_data,
        "join_requests": join_requests,
        "form":form,
        'query':query,
        'followers':followers,
        'following':following,
    }
    return render(request, "clubs/clan_dashboard.html", context)

def approve_reject(request):
    request_id = request.POST.get("request_id")
    action = request.POST.get("manage_request")
    join_request = get_object_or_404(ClanJoinRequest, id=request_id)
    if action == "approve":
        join_request.approve()
        return JsonResponse({"message": "Join request approved."})
    elif action == "reject":
        join_request.reject()
        return JsonResponse({"message": "Join request rejected."})
    return JsonResponse({"error": "Invalid request"}, status=400)

def add_remove_players(request):
    clan = get_object_or_404(Clans, id=request.session['clan_id'])
    form = AddPlayerToClanForm(request.POST or None,clan=clan)
    if request.method == "POST"  and form.is_valid():
        action = request.POST.get("action")
        print(action)
        player = form.cleaned_data.get("username")  # Get the selected user
        profile = get_object_or_404(Profile, user=player)
        if action == "add_player":
            if profile.clan:
                return JsonResponse({"message": f"{player.username} is already in a clan!"})

            profile.clan = clan  # Assign the player to the clan
            profile.save()
            return JsonResponse({"message": f"{player.username} has joined"})
        elif action == "remove_player":
            profile.clan = None  # Assign the player to the clan
            profile.save()
            return JsonResponse({"message": f"{player} has been removed from the clan."})
         
    return JsonResponse({"error": "Invalid request"}, status=400)

def club_follow_unfollow(request, action, followed_model, followed_id):
    """
    Allows a user or a club to follow or unfollow another user or club dynamically.
    :param action: "follow" or "unfollow"
    :param followed_id: ID of the entity being followed or unfollowed
    """
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
    if followed_model == "clan":
        followed_obj = get_object_or_404(Clans, id=followed_id)
    else:
        return JsonResponse({"error": "Invalid model type"}, status=400)
    followed_type = ContentType.objects.get_for_model(followed_obj)

    if action == "follow":
        follow, created = Follow.objects.get_or_create(
            follower_type=follower_type,
            follower_id=follower_id,
            followed_type=followed_type,
            followed_id=followed_obj.id
        )
        if created:
            return JsonResponse({"context": {"message": f"You are now following {followed_obj.clan_name}"}})
        return JsonResponse({"context": {"message":f"Already following {followed_obj.clan_name}"}})
    
    elif action == "unfollow":
        deleted, _ = Follow.objects.filter(
            follower_type=follower_type,
            follower_id=follower_id,
            followed_type=followed_type,
            followed_id=followed_obj.id
        ).delete()
        if deleted:
            return JsonResponse({"context": {"message": f"You have unfollowed {followed_obj.clan_name}"}})
        return JsonResponse({"context": {"message": "You weren't following this account"}})

    return JsonResponse({"error": "Invalid action"}, status=400)
